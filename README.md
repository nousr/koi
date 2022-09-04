# koi 🎣

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nousr/koi/blob/main/koi_colab_backend.ipynb) <a href="https://discord.gg/hDBbsXDd6K"><img alt="Join us on Discord" src="https://img.shields.io/discord/823813159592001537?color=5865F2&logo=discord&logoColor=white"></a>

koi is an open source plug-in that allows you to use AI to accelerate your art workflow!

#### Disclaimer ✋
> In the interest of getting the open source community on board--I have released this plug-in early. In its current state you may run into issues (particularly during the setup process). If you do, I encourage you to open an issue here on GitHub and describe your problems so that it can be fixed it for you and others!

---

## Overview 😄

> The goal of this repository is to serve as a starting point for building increasingly useful tools for artists of all levels of experience to use. 

[Link to original twitter thread](https://twitter.com/nousr_/status/1564797121412210688)

This plug-in serves as a working example of how new A.I. models like Stable Diffusion can lower the barrier of entry to art so that anyone can enjoy making their dreams a reality!

Because this is an open source project I encourage you to try it out, break things, and come back with suggestions!

## Getting Started 🏁

If you are new to git, or get stuck during the installation process, @Lewington-pitsos made a nice [step-by-step video](https://www.youtube.com/watch?v=rIhQakm4Efk).

The easiest way to get started is to follow the plug-in installation process for krita. Then use the google colab backend server *(button at the top of this readme)*! This should give you a good introduction to the setup process and get you up and running fast!

--- 

## Installation 🔨

### Krita has a few plug-in installation methods, however, I will refer you to the one I use.

- **Step 1**: Find your operating system's `pykrita` folder [reference](https://docs.krita.org/en/reference_manual/resource_management.html#resource-management)
- **Step 2**: Clone the repository, and copy the `koi` folder and `koi.desktop` to `pykrita`. (restart krita now if it is open)
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
  
> ***Note :raising_hand:***
>
> Before continuing, make sure you accept the terms of service for the `diffusers` model [link to do so here](https://huggingface.co/CompVis/stable-diffusion-v1-4).
>
> Next, inside your terminal run the `huggingface-cli login` command and paste a token generated from [here](https://huggingface.co/settings/tokens). If you don't want to repeat this step in the future you can then run `git config --global credential.helper store`. *(note: only do this on a computer you trust)*

  
- **Step 3**: Run the server by typing `python server.py`
  - If you did everything correctly you should see an adress spit out after some time (eg. 127.0.0.1:8888)
- **Step 4**: Open Krita, if you haven't already, and paste your address into the `endpoint` field of the plugin
  - You will also need to append the actual API endpoit you are using. By default this is `/api/img2img`
  - If you are using all of the default settings your endpoint field will look something like this `http://127.0.0.1:8888/api/img2img`

---

## Inference 🖌️
This part is easy!
- Step 1: Create a new canvas that is **512 x 512** (px) in size and make a **single-layer** sketch *(note: these are temporary restrictions)*.
- Step 2: Fill out the prompt field in the `koi` panel (default location is somewhere on the right of your screen).
- Step 3: Make any additional changes you would like to the inference parameters (strength, steps, etc)
- Step 4: Copy and paste your server's endpoint to the associated field
- Step 5: Click `dream`!

---

## FAQ ❔

- ***What does `koi` stand for?***
  - *Krita Open(source) Img2Img: While support for StableDiffusion is first, the goal is to have this plug-in be compatible with any model!*
- ***Why the client/server setup?***
  - *The goal is to make this as widely available as possible. The server can be run anywhere with a GPU (i.e. colab) and allow those with low-powered hardware to still use the plug-in!*
---

# TODO:
- [x] Add colab backend example
- [ ] Refactor code
- [ ] Add DreamStudio API support
- [ ] Add CI
- [ ] Improve documentation
- [ ] Add support for arbitrary canvas size & selection-based img2img
- [ ] Add support for masks
- [ ] Improve UI/UX
- [ ] Offer more configuration options
- [ ] Abstract away drop-in models for the server
