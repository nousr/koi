import json
from io import BytesIO

import click
from PIL import Image
from flask import Flask, Response, request, send_file
from flask_ngrok import run_with_ngrok

from koi_backend import harness

# init model
model = None

# init the flask server
app = Flask(__name__)


def header_to_sample_args(headers):
    """
    Convert HTTP headers to sample arguments.
    """

    arg_map = {
        "Sample-Steps": int,
        "Cond-Scale": float,
        "Batch-Size": int,
        "Image-Strength": float,
        "Precision": str,
        "Random-Seed": int,
        "Prompt": str,
    }

    args = {}

    for key, func in arg_map.items():
        args[key] = func(headers[key])

    return args


def data_to_pil(data):
    return Image.open(BytesIO(data))


def pil_to_data(image):
    """
    Store the image data in a file.
    """
    return_bytes = BytesIO()
    image.save(return_bytes, format="PNG")
    return_bytes.read()
    return_bytes.seek(0)

    return return_bytes


def get_contents(request, decode_method, as_json=False):
    """
    Return the data and headers of a request
    """

    headers = request.headers
    data = request.data

    if decode_method != "" and decode_method != None:
        data = data.decode(decode_method)

    if as_json:
        data = json.loads(data)

    return data, headers


@app.route("/api/model_select", methods=["POST"])
def change_model():
    """
    Change the model being used.

    API:
        request data should be json in the form of:
            {"model": f"{Model Harness Name}"}

    Returns:
        - status (Flask.Response): The status of your request...
            - status=100: if the model is already selected
            - status=200: if the model was sucessfully loaded
            - status=501: if the model does not exist as a harness
    """

    global model
    global request

    data, _ = get_contents(request=request, decode_method="utf-8", as_json=True)

    model_name = data["model"]

    # check to see if the model is already selected
    if model.__name__ == model_name:
        return Response(status=400)

    # check if that model exists
    if not hasattr(harness, model_name):
        click.secho("This model is not yet implemented.", fg="red")
        return Response(status=501)

    # otherise load the model
    model = getattr(harness, model_name)()


@app.route("/api/img2img", methods=["POST"])
def img2img():
    """
    Turn one sketch into different variations given a prompt.

    API:
        - HEADERS:
            - HTTP Headers + koi-compliant sample_args
        - DATA:
            - {"init_image": <sketch bytes>}
    """

    global model

    # get the image data and headers
    data, headers = get_contents(request, decode_method=None, as_json=False)

    print(headers)

    # get PIL image from data
    image = data_to_pil(data).convert("RGB")

    # hijack headers as the sample_args and inject image
    sample_args = header_to_sample_args(headers)
    sample_args.update({"Init-Image": image})

    # sample from model
    samples = model.img2img(sample_args=sample_args)

    # TODO: support multiple images being returned
    return_image = samples[0]

    image_bytes = pil_to_data(image=return_image)

    return send_file(file=image_bytes, mimetype="image/png")


@app.route("/api/txt2img", methods=["POST"])
def txt2img():
    """
    Turn a prompt into an image.
    """
    raise NotImplementedError


@app.route("/api/inpaint", methods=["POST"])
def inpaint():
    """
    Modify an existing image.
    """
    raise NotImplementedError


@click.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8888)
@click.option("--use-ngrok", default=False)
@click.option("--sd-checkpoint-path", default=None)
@click.option("--sd-config-path", default=None)
def main(host, port, use_ngrok, sd_checkpoint_path, sd_config_path):
    """
    Initialize the server and enter a forever-loop to listen for requests.
    """

    global model

    click.secho(f"Loading Default Model...", fg="yellow")
    model = harness.StableDiffusionHarness(checkpoint_path=sd_checkpoint_path, config_path=sd_config_path)
    click.secho("Done!", fg="green")

    if use_ngrok:
        run_with_ngrok(app)
        app.run()

    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
