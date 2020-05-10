# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python (halite)
#     language: python
#     name: halite
# ---

# %load_ext autoreload
# %autoreload 2
import sys


sys.path.append("..")

import kaggle_environments
from kaggle_environments import make
from kaggle_environments.agent import Agent
from halite.agents.agent import make_agent


env = make("halite")
_ = env.reset()
state = env.state



# Seems like the environment has its own internal definition of a game Board, that its default random agent uses.
# Copy pasted here, but Jan is working on something better.
#
# The way the kaggle env works is that their wrapper just imports interpreter and runs it.

# Making agents
# ------------

# The kaggle submission process involves uploading a single file submission to their servers, where the final callable (a function) is extracted and run as your agent. This complicates things if you have lots of different files in your project. The solution we use is thee Stickytape package, which generates a standalone file by analysing the imports in files.
#
# There is a catch: if you have multiple agent designs, and you import them all in your submission, then stickytape will package them all up, leading to significant bloat. This might be an issue if you are uploading extra data such as a hash table or model parameters, as kaggle typically sets a size limit on your uploads.
#
# To get around this, we provide an agent factory function that dynamically imports agents from submodules in halite.agents. The only requirement is that these submodules expose a class with the name Agent (this is typically done in `__init__.py` by adding the line `from .agent import MyAgentname as Agent`). 
#

agent = make_agent("depressed_agent", env.configuration)

# __Important note__: make_agent() returns a function, not a class instance. This is because the Kaggle API only accepts functions. Class methods are not valid either.

# Playing games
# -------------
#
# Use make_agent() to import/instantiate any agents you want to pit against each other.

agent1 = make_agent("depressed_agent", env.configuration)
agent2 = make_agent("random_agent", env.configuration)
agent3 = make_agent("random_agent", env.configuration)

# There are several ways to run a game. The first is env.run(), which accepts a list of agents. There is also a default "random" agent, which can be referred to using a string (there is an internal registry of Kaggle agents, so far "random" is the only one. Matches must consist of 1, 2, or 4 agents.
#
# env.run() runs an entire game, non-interactively.

states = env.run([agent1, agent2, agent3, 'random'])

# To view the output, the env.render() method can be used. To get decent video output in jupyter, use the `mode='ipython'` option.

env.render(mode="ipython", width=500,height=600)

# Interactive games
# -------------
#
# There are two main ways to give your actions step-by-step. The API exposes the `env.play()` and `env.train()` methods in order to allow for interactive play. Both functions accept a list of agents as before, but one of the agents must be a `None`. This marks the agent that will be played interactively.
#
# There is a key difference between the two methods: 
# * `env.train()` returns a new object (which is actually just a Kaggle struct) that contains its own `reset()` and `step()` functions. These functions can then be used to run the game step by step, only supplying the actions for the interactive agent.
# * `env.play()` allows for human interaction through the browser. First it clones the environment, creating a new object. It then calls `env.train()` on the new environment, adding the resulting `{step: step(), reset: reset() }` struct to a dict called `interactives` in the `kaggle_environments` top-level namespace. The game viewer javascript then accesses this object to return any actions from a human player (from button presses etc). The Halite env has no available interactions as of now (its a bit complicated for human players), so this mode is useless right now.
#
# Unfortunately there doesn't seem to be a way to watch the game as it unfolds when using env.train(). But heres how you can use it:

trainer = env.train([None, "random"])

# +
done = False
obs = trainer.reset()

while not done:
    actions = agent1(obs)
    obs, reward, done, info = trainer.step(actions)
env.render(mode="ipython", width=500,height=600)
    
