# koi 🎣

koi is an open source plug-in that allows you to use AI to accelerate your art workflow!

#### Disclaimer ✋
> In the interest of getting the open source community on board--I have released this plug-in early. In its current state you may run into issues (particularly during the setup process). If you do, I encourage you to open an issue here on GitHub and describe your problems so that it can be fixed it for you and others!

---

## Overview 😄

> The goal of this repository is to serve as a starting point for building increasingly useful tools for artists of all levels of experience to use. 

This plug-in serves as a working example of how new A.I. models like Stable Diffusion can lower the barrier of entry to art so that anyone can enjoy making their dreams a reality!

Because this is an open source project I encourage you to try it out, break things, and come back with suggestions!

## Installation 🔨

### Krita has a few plug-in installation methods, however, I will refer you to the one I use.

- **Step 1**: Find your operating system's `pykrita` folder [reference](https://docs.krita.org/en/reference_manual/resource_management.html#resource-management)
- **Step 2**: Copy the `koi` folder, as well as `koi.desktop` to `pykrita`.
- **Step 3**: Open Krita and navigate to the python plug-in menu [reference](https://scripting.krita.org/lessons/plugins-introduction)
- **Step 4**: Enable the `koi` plugin and restart Krita to load the plug-in.

### The next thing you will need to do is setup the backend server that do all the computation!

- **Step 0**: Ensure you have a GPU-accelerated installation of `pytorch`. *(You can skip this step if you are using colab or already have it)*
  - Follow the installation instructions on pytorch's official [getting started](https://pytorch.org/get-started/locally/).
- **Step 1**: Get the latest version of huggingface's `diffusers` from source by going to the [github repo](https://github.com/huggingface/diffusers)
  - From here you can clone the repo `git clone https://github.com/huggingface/diffusers.git` & `cd diffusers` to move into the directory.
  - Install the package with `pip install -e .`
  
- **Step 2**: Install this package! I recommend moving out of the diffusers folder if you haven't already (eg. `cd ..`)
  - `git clone https://github.com/nousr/koi.git`, then  `cd koi` and `pip install -e .`
- **Step 3**: Run the server by typing `python server.py`
  - If you did everything correctly you should see an adress spit out after some time (eg. 127.0.0.1:8888)
- **Step 4**: Open Krita, if you haven't already, and paste your address into the `endpoint` field of the plugin
  - You will also need to append the actual API endpoit you are using. By default this is `/api/img2img`
  - If you are using all of the default settings your endpoint field will look something like this `http://127.0.0.1:8888/api/img2img`

## Inference 🖌️
This part is easy!
- Step 1: Create a new canvas that is **512 x 512** (px) in size and make a **single-layer** sketch *(note: these are temporary restrictions)*.
- Step 2: Fill out the prompt field in the `koi` panel (default location is somewhere on the right of your screen).
- Step 3: Make any additional changes you would like to the inference parameters (strength, steps, etc)
- Step 4: Copy and paste your server's endpoint to the associated field
- Step 5: Click `dream`!


## FAQ ❔

- ***What does `koi` stand for?***
  - *Krita Open(source) Img2Img: While support for StableDiffusion is first, the goal is to have this plug-in be compatible with any model!*
- ***Why the client/server setup?***
  - *The goal is to make this as widely available as possible. The server can be run anywhere with a GPU (i.e. colab) and allow those with low-powered hardware to still use the plug-in!*
---

# TODO:
- [ ] Refactor code
- [ ] Add DreamStudio API support
- [ ] Add CI
- [ ] Improve documentation
- [ ] Add support for arbitrary canvas size & selection-based img2img
- [ ] Add support for masks
- [ ] Improve UI/UX
- [ ] Offer more configuration options
- [ ] Abstract away drop-in models for the server
