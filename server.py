from urllib import request
from flask import Flask, Response, request, send_file
from PIL import Image
from io import BytesIO
from torch import autocast
from diffusers import StableDiffusionImg2ImgPipeline
from click import secho

# TODO: add command line arguments

secho("Loading Model...", fg="yellow")

# FIXME: more elegant model scope
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", use_auth_token=True
).to("cuda")

secho("Finished!", fg="green")

app = Flask(__name__)


@app.route("/api/img2img", methods=["POST"])
def img2img():
    global pipe

    r = request
    headers = r.headers

    data = r.data
    buff = BytesIO(data)
    img = Image.open(buff).convert("RGB")

    # remove alpha channel from image

    with autocast("cuda"):
        return_image = pipe(
            init_image=img,
            prompt=headers["prompt"],
            strength=float(headers["image_strength"]),
            guidance_scale=float(headers["prompt_strength"]),
            num_inference_steps=int(headers["steps"]),
        )["sample"][0]

    return_bytes = BytesIO()
    return_image.save(return_bytes, format="JPEG")
    return_bytes.read()
    return_bytes.seek(0)

    return send_file(return_bytes, mimetype="image/jpeg")


app.run(host="0.0.0.0", port=8888)
