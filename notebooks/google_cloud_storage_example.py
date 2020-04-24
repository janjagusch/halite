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

import sys
sys.path.append("..")

from typing import Dict, Union, Callable, Tuple, List
import json
import gzip

from google.cloud import storage, bigquery

from kaggle_environments import make, Environment
import numpy as np

from halite.utils import camel_to_snake

env = make("halite")
_ = env.reset(num_agents=4)
_ = env.run(["random", "random", "random", "random"])


def upload_to_google_cloud_storage(env: Environment, bucket: str = "kaggle-halite"):
    """
    Uploads a gzipped JSON representation of the environment to Google Cloud Storage.
    """
    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.blob(f"replays/{env.id}.json.gzip")
    blob.upload_from_string(gzip.compress(json.dumps(env.toJSON()).encode("ascii")))


def placements(env):
    # Dumb placement calculator. This should be improved.
    rewards = np.array([-1 if state.reward is None else state.reward for state in env.steps[-1]])
    return (np.argsort(-rewards).astype(int) + 1).tolist()


def run(env: Environment, players: List[Tuple[str, Union[str, Callable]]], upload_to_gcs=False, tags=None):
    
    _ = env.reset(num_agents=len(players))    
    _ = env.run([player[1] for player in players])
    
    if not upload_to_gcs:
        return env
    
    upload_to_google_cloud_storage(env)
    
    dim_game = {
        "id": env.id,
        "configuration": {camel_to_snake(key): value for key, value in env.configuration.items()},
        "players": len(env.state[0].observation.players),
        "tags": tags or []
    }
    
    dim_player = [
        {
            "game_id": env.id,
            "player_id": i,
            "agent_id": player[0],
            "placement": placement,
        }
        for i, (player, placement) in enumerate(zip(players, placements(env)))
    ]
    
    client = bigquery.Client()
    dataset = bigquery.dataset.DatasetReference.from_string("kaggle-halite.halite_analytics")
    
    table = bigquery.dataset.DatasetReference.from_string(f"kaggle-halite.halite_analytics").table("dim_game")
    errors = client.insert_rows(client.get_table(table), [dim_game])
    print(errors)
    
    table = bigquery.dataset.DatasetReference.from_string(f"kaggle-halite.halite_analytics").table("dim_player")
    errors = client.insert_rows(client.get_table(table), dim_player)
    print(errors)
    
    return env


players = [
    ("random", "random"),
    ("random", "random"),
    ("random", "random"),
    ("random", "random"),
]

run(env, players, upload_to_gcs=True)
