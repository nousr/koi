import torch
from urllib import request
from flask import Flask, Response, request, send_file
from PIL import Image
from io import BytesIO
from torch import autocast
from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionPipeline
from click import secho
from zipfile import ZipFile

# TODO: add command line arguments

secho("Loading Model...", fg="yellow")

MODEL = "stabilityai/stable-diffusion-2-1"

params = dict(
    use_auth_token=True,
    # TODO: detect if there's 8G VRAM before we enable this model
    revision="fp16",
    torch_dtype=torch.float16,
    safety_checker=None,
    requires_safety_checker=False,
)

# FIXME: more elegant model scope
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(MODEL, **params).to("cuda")

text_pipe = StableDiffusionPipeline.from_pretrained(MODEL, **params).to("cuda")

secho("Model Loaded!", fg="green")

app = Flask(__name__)

def get_name(prompt, seed):
  return f'{prompt}-{seed}'

def seed_everything(seed: int):
    import random, os

    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True

def is_one_color(image):
    # https://stackoverflow.com/a/28915260/2234013
    colors = image.getcolors()
    print(colors)
    return len(colors) == 1

@app.route("/api/img2img", methods=["POST"])
def img2img():
    global pipe
    global text_pipe

    headers = request.headers
    data = request.data

    buff = BytesIO(data)
    img = Image.open(buff).convert("RGB")
    print(type(img))

    seed = int(headers["seed"])
    prompt = headers['prompt']
    variant_count = int(headers.get('variations', 1) or 1)

    zip_stream = BytesIO()
    with ZipFile(zip_stream, 'w') as zf:
        # TODO num_images_per_prompt results in memory issues easily
        # num_images_per_prompt=variant_count
        for index in range(variant_count):
            variant_seed = seed + index
            seed_everything(variant_seed)

            if is_one_color(img):
                secho('Image is empty – generating with txt2img')
                diffusion_results = text_pipe(
                    prompt=prompt,
                    guidance_scale=float(headers["prompt_strength"]),
                    num_inference_steps=int(headers["steps"]),
                    width=512,
                    height=512
                )
            else:
                diffusion_results = pipe(
                    image=img,
                    prompt=prompt,
                    strength=float(headers["sketch_strength"]),
                    guidance_scale=float(headers["prompt_strength"]),
                    num_inference_steps=int(headers["steps"]),
                )
            return_image = diffusion_results.images[0]
            return_bytes = BytesIO()
            return_image.save(return_bytes, format="JPEG")

            return_bytes.seek(0)
            zf.writestr(get_name(prompt, variant_seed), return_bytes.read())

    zip_stream.seek(0)

    return send_file(zip_stream, mimetype="application/zip")


app.run(host="0.0.0.0", port=8888)
