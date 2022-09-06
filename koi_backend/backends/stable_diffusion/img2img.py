"""
references:
    - https://github.com/CompVis/stable-diffusion/blob/main/scripts/img2img.py
    - https://github.com/hlky/stable-diffusion/blob/main/scripts/img2img.py
"""

from contextlib import nullcontext
from random import sample

import k_samplers
import numpy as np
import torch
from einops import rearrange, repeat
from PIL import Image
from torch import autocast


def exists(x):
    return x is not None


def preprocess_image(image: Image):
    """
    Process the image so that it makes sense to stable diffusion.
    """

    w, h = image.size
    w, h = map(lambda x: x - x % 32, (w, h))  # resize to integer multiple of 32
    image = image.resize((w, h), resample=Image.Resampling.LANCZOS)
    image = np.array(image).astype(np.float32) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)

    return image


def get_init_latent(init_image, batch_size, model):
    """
    Get the first stage encoding of an init image.
    """

    init_image = repeat(init_image, "1 ... -> b ...", b=batch_size)
    return model.get_first_stage_encoding(model.encode_first_stage(init_image))


def get_sampler(sampler_name):
    """
    Retrieve the requested sampler from k_samplers.
    """

    sampler_name += "sample_"
    assert hasattr(k_samplers, sampler_name), "This sampler does not exist."
    return getattr(k_samplers, sampler_name)


@torch.no_grad()
def img2img(model, sample_args):
    """
    IMG2IMG

    Turns one image into another.

    Inputs:
        - model (torch.nn.module): A CompVis compatible model to sample from.
        - sample_args (dict): KOI compliant sample arguments.

    Returns:
        - samples (list[PIL.Image]): Output images.
        - error (str): Error message describing what went wrong.
    """
    if not exists(sample_args["init_image"]):
        return None

    # prepare model
    wrapped_model = k_samplers.CompVisDenoiser(model)

    # prepare the init image
    init_image = preprocess_image(sample_args["init_image"])
    x0 = get_init_latent(init_image=init_image, batch_size=int(sample_args["batch_size"]), model=model)

    # get the sampler
    sampler = get_sampler(sampler_name=sample_args["sampler"])

    # strength
    if not (0.0 <= sample_args["image_strength"] <= 1.0):
        return "Image strength given was out of range"

    t_enc = int(sample_args["image_strength"] * sample_args["sample_steps"])

    # context
    precision_scope = autocast if sample_args["precision"] == "autocast" else nullcontext

    # set seed
    torch.manual_seed(sample_args["random_seed"])

    # keep track of all samples
    samples = []

    with precision_scope():
        with model.ema_scope():

            # get learned conditioning
            uc = None
            if sample_args["cond_scale"] != 1.0:
                uc = model.get_learned_conditioning(sample_args["batch_Size"] * [""])
            c = model.get_learned_conditioning(sample_args["prompt"])

            # setup
            sigmas = wrapped_model.get_sigmas(sample_args["sample_steps"])
            noise = torch.randn_like(x0) * sigmas[sample_args["sample_steps"] - t_enc - 1]
            xi = x0 + noise
            sigma_sched = sigmas[sample_args["sample_steps"] - t_enc - 1 :]
            model_wrap_cfg = k_samplers.CFGDenoiser(wrapped_model)
            extra_args = {"cond": c, "uncond": uc, "cond_scale": sample_args["cond_scale"]}

            # sample
            samples_ddim = sampler(model_wrap_cfg, xi, sigma_sched, extra_args=extra_args)

            # decode results
            x_samples_ddim = model.decode_first_stage(samples_ddim)
            x_samples_ddim = torch.clamp((x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0)

            for x_sample in x_samples_ddim:
                # scale to proper pixel values & convert to PIL Image
                x_sample = 255.0 * rearrange(x_sample.detach().cpu().numpy(), "c h w -> h w c")
                samples.append(Image.fromarray(x_sample.astype(np.uint8)))

    return samples