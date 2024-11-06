# syntax=docker/dockerfile:1
# BASE IMAGE FOR COMMON DEPENDENCIES / ENV
FROM python:3.12-slim AS base

    # python
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    # create venv ourselves
    POETRY_VIRTUALENVS_CREATE=false \
    VIRTUAL_ENV="/venv"

# add poetry/venv to PATH, then prepare it
ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV


# BUILDER IMAGE FOR INSTALLING DEPENDENCIES
FROM base AS builder

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        build-essential

# install poetry using set env variables
# mount so cache is saved
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python -

WORKDIR /app
COPY poetry.lock pyproject.toml ./
# install dependencies
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main


# FINAL IMAGE USED DURING PRODUCTION
FROM base AS runtime

COPY --from=builder $POETRY_HOME $POETRY_HOME
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app
COPY poetry.lock pyproject.toml ./
COPY ./bloom ./bloom
COPY .env ./.env

ENTRYPOINT [ "/entrypoint.sh"]
CMD [ "python3", "bloom/bot.py"]