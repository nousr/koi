"""
Abstract away model loading.
"""

from koi_backend.backends import stable_diffusion


class ModelHarness:
    def __init__(self, name) -> None:
        self.name = name

    def load_model(self):
        raise NotImplementedError

    def img2img(self):
        raise NotImplementedError

    def txt2img(self):
        raise NotImplementedError

    def inpaint(self):
        raise NotImplementedError


class StableDiffusionHarness(ModelHarness):
    def __init__(self, checkpoint_path=None, config_path=None) -> None:
        super().__init__(name="StableDiffusion V-1.4")
        self.model = self.load_model(
            checkpoint_path=checkpoint_path, config_path=config_path
        )

    def load_model(self, checkpoint_path=None, config_path=None):
        return stable_diffusion.load(
            checkpoint_path=checkpoint_path, config_path=config_path
        )

    def img2img(self, sample_args):
        return stable_diffusion.img2img(model=self.model, sample_args=sample_args)
