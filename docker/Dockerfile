FROM python:3.12-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev  # respects

FROM python-base as runtime

COPY --from=builder-base $VENV_PATH $VENV_PATH

COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./bloom /app/bloom
COPY .env /app/.env
WORKDIR /app

ENTRYPOINT /entrypoint.sh $0 $@
CMD [ "python3", "bloom/bot.py"]