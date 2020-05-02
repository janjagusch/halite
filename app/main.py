"""
This module serves the submission through a FastAPI.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from kaggle_environments.utils import Struct

from submission import act


class Environment(BaseModel):
    observation: dict
    configuration: dict


app = FastAPI()


@app.post("/act")
async def act_(environment: Environment):
    observation = Struct(**environment.observation)
    configuration = Struct(**environment.configuration)
    return act(observation, configuration)
