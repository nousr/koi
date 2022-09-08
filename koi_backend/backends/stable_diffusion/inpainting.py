import k_samplers
import numpy as np
import torch
from PIL import Image


def exists(x):
    return x is not None


class CFGDenoiser(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.inner_model = model

    def forward(self, x, sigma, uncond, cond, cond_scale):
        x_in = torch.cat([x] * 2)
        sigma_in = torch.cat([sigma] * 2)
        cond_in = torch.cat([uncond, cond])
        uncond, cond = self.inner_model(x_in, sigma_in, cond=cond_in).chunk(2)
        return uncond + (cond - uncond) * cond_scale


def get_sampler(sampler_name):
    """
    Retrieve the requested sampler from k_samplers.
    """

    sampler_name = "sample_" + sampler_name
    assert hasattr(
        k_samplers.sampling, sampler_name
    ), f"The {sampler_name} sampler does not exist."
    return getattr(k_samplers.sampling, sampler_name)


def make_batch(image, mask, device="cuda"):
    image = np.array(Image.open(image).convert("RGB"))
    image = image.astype(np.float32) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)

    mask = np.array(Image.open(mask).convert("L"))
    mask = mask.astype(np.float32) / 255.0
    mask = mask[None, None]
    mask[mask < 0.5] = 0
    mask[mask >= 0.5] = 1
    mask = torch.from_numpy(mask)

    masked_image = (1 - mask) * image

    batch = {"image": image, "mask": mask, "masked_image": masked_image}
    for k in batch:
        batch[k] = batch[k].to(device=device)
        batch[k] = batch[k] * 2.0 - 1.0
    return batch


@torch.no_grad()
def inpaint(model, sample_args):

    # extract inputs
    mask = sample_args["Mask"]
    image = sample_args["Init-Image"]

    # wrap model for use with k_samplers
    wrapped_model = k_samplers.external.CompVisDenoiser(model)

    # get the sampler
    sampler = get_sampler(sampler_name=sample_args["Sampler"])

    with model.ema_scope():
        # make the image/mask batch to pass to the model
        batch = make_batch(image, mask)

        # encode masked image and concat downsampled mask
        c = wrapped_model.cond_stage_model.encode(batch["masked_image"])
        cc = torch.nn.functional.interpolate(batch["mask"], size=c.shape[-2:])
        c = torch.cat((c, cc), dim=1)

        shape = (c.shape[1] - 1,) + c.shape[2:]
        samples_ddim, _ = sampler.sample(
            S=sample_args["Sample-Steps"],
            conditioning=c,
            batch_size=c.shape[0],
            shape=shape,
            verbose=False,
        )

        x_samples_ddim = wrapped_model.decode_first_stage(samples_ddim)

        image = torch.clamp((batch["image"] + 1.0) / 2.0, min=0.0, max=1.0)
        mask = torch.clamp((batch["mask"] + 1.0) / 2.0, min=0.0, max=1.0)
        predicted_image = torch.clamp((x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0)

        inpainted = (1 - mask) * image + mask * predicted_image
        inpainted = inpainted.cpu().numpy().transpose(0, 2, 3, 1)[0] * 255
