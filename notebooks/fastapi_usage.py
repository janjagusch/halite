# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python (halite)
#     language: python
#     name: halite
# ---

# # FastAPI Usage

# 1. Build the container:
# ```sh
# docker build -t halite:latest -f Dockerfile .
# ```
#
#
# 2. Run the container:
# ```sh
# docker run --publish 8080:80 halite
# ```

from kaggle_environments import make
import requests

env = make("halite")


def act(url, observation, configuration):
    """
    Sends a post request to one of the two agents.
    """
    data = {"observation": observation, "configuration": configuration}
    return requests.post(url=url, json=data).json()


URL = "http://localhost:8080/act"
OBS = env.state[0].observation
CONFIG = env.configuration

res = act(URL, OBS, CONFIG)

res
