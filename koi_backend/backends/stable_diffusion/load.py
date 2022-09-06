import os
from omegaconf import OmegaConf
from koi_backend.backends.stable_diffusion.utils import load_model_from_config

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_LOCATION = os.path.join(PACKAGE_DIR, "configs", "v1-inference.yaml")
DEFAULT_CHECKPOINT_LOCATION = os.path.join(PACKAGE_DIR, "models", "sd-v1-4.ckpt")


def load(config_path=DEFAULT_CONFIG_LOCATION, checkpoint_path=DEFAULT_CHECKPOINT_LOCATION):
    config = OmegaConf.load(config_path)
    model = load_model_from_config(config=config, ckpt=checkpoint_path)

    return model
