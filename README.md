# koi 🎣

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nousr/koi/blob/main/koi_colab_backend.ipynb) <a href="https://discord.gg/hDBbsXDd6K"><img alt="Join us on Discord" src="https://img.shields.io/discord/1015817150608453732?color=5865F2&logo=discord&logoColor=white"></a> [![GitHub](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com/nousr/koi)

---

# Development Branch

You are now on the development branch.

**This branch has many new features...but will require a stronger GPU to use** (optimized versions of stable diffusion are not yet supported).

---

# Installation

Step 1: Download and install [anaconda](https://www.anaconda.com/)

Step 2: Clone this repository using git (or download as a zip and extract it somewhere on your computer)

Step 3: Navigate to the koi project folder (using your anaconda-enabled terminal) and run the following command

`conda env create -f environment.yaml`

Step 4: Copy the contents of the `pykrita` folder to your operating system's `pykrita` folder. You can find out where that is located [here](https://docs.krita.org/en/reference_manual/resource_management.html#resource-management)

# Launching

To launch the backend server you can either use google colab or navigate to `koi_backend` and run the server locally with

`python server.py`

> use `python server.py --help` for more info on the available options.

# Bugs
If you run into any bugs using this branch please include:
  - Open your issue with a `[DEV]` tag in your title to differentiate between issues with the stable branch.
  - The error recieved inside of Krita
  - The error recieved inside of your backend server (colab/local)
  - Your version of krita