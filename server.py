import torch
from urllib import request
from flask import Flask, Response, request, send_file
from PIL import Image
from io import BytesIO
from torch import autocast
from diffusers import StableDiffusionImg2ImgPipeline
from click import secho
from zipfile import ZipFile

# TODO: add command line arguments

secho("Loading Model...", fg="yellow")

# FIXME: more elegant model scope
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-5", use_auth_token=True,
    revision="fp16",
    torch_dtype=torch.float16,
    safety_checker=None,
    requires_safety_checker=False,
).to("cuda")

secho("Finished!", fg="green")

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

@app.route("/api/img2img", methods=["POST"])
def img2img():
    global pipe

    r = request
    headers = r.headers

    data = r.data
    buff = BytesIO(data)
    img = Image.open(buff).convert("RGB")

    seed = int(headers["seed"])
    prompt = headers['prompt']


    print(r.headers)

    zip_stream = BytesIO()
    with ZipFile(zip_stream, 'w') as zf:

        for index in range(int(headers['variations'])):
            variation_seed = seed + index
            seed_everything(variation_seed)
        
            with autocast("cuda"):
                return_image = pipe(
                    init_image=img,
                    prompt=prompt,
                    strength=float(headers["sketch_strength"]),
                    guidance_scale=float(headers["prompt_strength"]),
                    num_inference_steps=int(headers["steps"]),
                ).images[0]


            return_bytes = BytesIO()
            return_image.save(return_bytes, format="JPEG")

            return_bytes.seek(0)
            zf.writestr(get_name(prompt, variation_seed), return_bytes.read())

    zip_stream.seek(0)

    return send_file(zip_stream, mimetype="application/zip")


app.run(host="0.0.0.0", port=8888)
