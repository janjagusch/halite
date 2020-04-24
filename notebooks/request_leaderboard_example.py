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

# # Requesting the Leaderboard

import sys
sys.path.append("..")

from datetime import datetime
from tempfile import TemporaryDirectory

from google.cloud import bigquery
from kaggle import KaggleApi
import pandas as pd
import pandas_gbq

api = KaggleApi()
api.authenticate()

# +
COMPETITION = "connectx"
TOP = 100

with TemporaryDirectory() as tmp_dir:
    api.competition_leaderboard_download(COMPETITION, tmp_dir)
    leaderboard = pd.read_csv(f"{tmp_dir}/{COMPETITION}.zip").head(100)
    leaderboard.columns = ["team_id", "team_name", "submitted_at", "score"]
    leaderboard["placement"] = leaderboard.index + 1
    leaderboard["requested_at"] = datetime.now()

# +
client = bigquery.Client()
dataset = bigquery.dataset.DatasetReference.from_string("kaggle-halite.halite_analytics")

table = bigquery.dataset.DatasetReference.from_string(f"kaggle-halite.halite_analytics").table("leaderboard")
errors = client.insert_rows(client.get_table(table), leaderboard.to_dict(orient="records"))

assert not errors
