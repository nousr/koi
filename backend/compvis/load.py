from omegaconf import OmegaConf
from compvis.utils import load_model_from_config

DEFAULT_CONFIG_LOCATION = "configs/stable-diffusion/v1-inference.yaml"
DEFAULT_CHECKPOINT_LOCATION = "models/sd-v1-4.ckpt"
def load_v1_model(config_path=DEFAULT_CONFIG_LOCATION, checkpoint_path=DEFAULT_CHECKPOINT_LOCATION):
    config = OmegaConf.load(config_path)
    model = load_model_from_config(config=config, ckpt=checkpoint_path)
    return model

