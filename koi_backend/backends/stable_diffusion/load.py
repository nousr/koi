import os
import sys

from click import secho
from koi_backend.backends.stable_diffusion.utils import load_model_from_config
from omegaconf import OmegaConf

sys.path.append(os.getcwd())

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_LOCATION = os.path.join(PACKAGE_DIR, "configs", "v1-inference.yaml")
DEFAULT_CHECKPOINT_LOCATION = os.path.join(PACKAGE_DIR, "models", "sd-v1-4.ckpt")


def load(config_path=None, checkpoint_path=None):

    if config_path is None:
        config_path = DEFAULT_CONFIG_LOCATION

    if checkpoint_path is None:
        checkpoint_path = DEFAULT_CHECKPOINT_LOCATION

    # verify that the files exist
    if not os.path.exists(DEFAULT_CHECKPOINT_LOCATION):
        secho("CHECKPOINT MISSING!", fg="red")
        secho(
            f"Hint: ensure your stable diffusion checkpoint is placed in {checkpoint_path} and named 'sd-v1-4.ckpt'",
            fg="red",
        )

        exit(1)

    config = OmegaConf.load(config_path)
    model = load_model_from_config(config=config, ckpt=checkpoint_path)

    return model
