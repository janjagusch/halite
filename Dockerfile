FROM python:3.7-slim-stretch AS build-env

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION="1.0.2"

RUN set -ex \
    && apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y libev-dev g++ curl git \
    && curl -sSL \
    https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

WORKDIR /usr/src/app

COPY ./pyproject.toml .
COPY ./poetry.lock .

RUN . $HOME/.poetry/env \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8

COPY --from=build-env /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages

COPY ./app /app
COPY ./submission.py /app/submission.py
