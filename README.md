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

- Step 1: Find your operating system's `pykrita` folder [reference](https://docs.krita.org/en/reference_manual/resource_management.html#resource-management)
- Step 2: Copy the `koi` folder, as well as `koi.desktop` to `pykrita`.
- Step 3: Open Krita and navigate to the python plug-in menu [reference](https://scripting.krita.org/lessons/plugins-introduction)
- Step 4: Enable the `koi` plugin and restart Krita to load the plug-in.

### The next thing you will need to do is setup the backend server that do all the computation!

:warning: (Under Construction) 
- **TLDR; have the libraries installed, a cuda gpu, and run the server.**
- I will update this repository with an official `requirements` list to aid in the installation process. For now, though it may require some previous knowledge to get working!

## Inference 🖌️
This part is easy!
- Step 1: Create a new canvas that is **512pxx512px** and make a **single-layer** sketch *(note: these are temporary restrictions)*.
- Step 2: Fill out the prompt field in the `koi` panel (default location is somewhere on the right of your screen).
- Step 3: Make any additional changes you would like to the inference parameters (strength, steps, etc)
- Step 4: Copy and paste your server's endpoint to the associated field
- Step 5: Click `dream`!

---

# TODO:
- [ ] Refactor code
- [ ] Add CI
- [ ] Improve documentation
- [ ] Add support for arbitrary canvas size & selection-based img2img
- [ ] Add support for masks
- [ ] Improve UI/UX
- [ ] Offer more configuration options
- [ ] Abstract away drop-in models for the server
