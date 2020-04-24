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
#     name: connect-x
# ---

# # Uploading an Environment to Google Cloud Storage

# Requirements, you have installed the Google Cloud SDK and have authenticated yourself.

import json
import gzip

from google.cloud import storage

from kaggle_environments import make

env = make("halite")
_ = env.reset(num_agents=4)
_ = env.run(["random", "random", "random", "random"])

client = storage.Client()
bucket = client.bucket("kaggle-halite")
blob = bucket.blob(f"replays/{env.id}.json.gzip")
blob.upload_from_string(gzip.compress(json.dumps(env.toJSON()).encode("ascii")))
