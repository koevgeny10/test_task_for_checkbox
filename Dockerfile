ARG POETRY_KEYS
ARG TEMP_DIR=opt/temp
ARG WHEELS_DIR=${TEMP_DIR}/wheels
ARG APP_DIR=opt/app
ARG DELETE_APT_LISTS="rm -rf /var/lib/apt/lists/*"

FROM python:3.12-slim-bullseye AS base

ARG DELETE_APT_LISTS

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    curl \
    && ${DELETE_APT_LISTS}
RUN python -m pip install --upgrade pip

FROM base AS base_builder

ARG TEMP_DIR

WORKDIR /${TEMP_DIR}

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - --version 1.8.1
ENV PATH="/etc/poetry/bin:${PATH}"
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

FROM base_builder AS builder

ARG POETRY_KEYS
ARG WHEELS_DIR

RUN poetry export ${POETRY_KEYS} -f requirements.txt --output requirements.txt --without-hashes \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /${WHEELS_DIR} -r requirements.txt \
    && rm requirements.txt

FROM base AS src

ARG WHEELS_DIR
ARG APP_DIR

COPY --from=builder /${WHEELS_DIR}/ /${WHEELS_DIR}

RUN pip install --no-cache /${WHEELS_DIR}/*

WORKDIR /${APP_DIR}

COPY checks checks

FROM src AS not_root_user

RUN addgroup --system app && adduser --system --group app
USER app
ENV PATH="/home/app/.local/bin:${PATH}"

FROM not_root_user AS api

#WORKDIR /${APP_DIR}/checks
ENV PYTHONPATH="/${APP_DIR}/checks:${PYTHONPATH}"

ENTRYPOINT [ "uvicorn", "checks.api:app", "--host", "0.0.0.0", "--port", "80", "--loop", "uvloop" ]

HEALTHCHECK --interval=5s --start-period=20s CMD [ "curl", "-f", "http://localhost/health/" ]

FROM api AS prod

CMD [ "--workers", "2" ]

FROM api AS dev

ENV WATCHFILES_FORCE_POLLING=true

#RUN apt-get update \
#    && apt-get install -y \
#    htop \
#    mc \
#    && rm -rf /var/lib/apt/lists/*

CMD [ "--reload" ]

FROM src AS migrations

COPY alembic.ini .
COPY migrations migrations

ENTRYPOINT ["bash"]

FROM migrations AS tests

ARG APP_DIR
ARG JWT_KEYS_DIR=${APP_DIR}/jwt
ARG PRIVATE_KEY_FILE=${JWT_KEYS_DIR}/jwtRS256.key
ARG PUBLIC_KEY_FILE=${PRIVATE_KEY_FILE}.pub

ENV DEBUG=0
ENV JWT_SIGNING_ALGORITHM=RS256
ENV JWT_LIFETIME_MINUTES=30

RUN mkdir /${JWT_KEYS_DIR} \
    && touch /${PRIVATE_KEY_FILE} \
    && touch /${PUBLIC_KEY_FILE} \
    && echo -e "-----BEGIN RSA PRIVATE KEY-----\nMIICXgIBAAKBgQDPXrBE8P6svSDu3lb1akbhyHIBJ0/1vEQlURE5uTySRRs7wpHI\n40Oo9R7W9Yx/wcoXKzIOkz5+fjMoZrfwDz8mse5kaddc08DUXyxjW3k3VujYDPyj\nSJvp34rdjeTfHog/dPHKmF7vlTb3UO5QdIY6bi5CSJlnFearX1dkwkpD8wIDAQAB\nAoGBAKkO5BvAcY/4PIIhB7naI+Fsnezs1NZc3x2hIq7xoj0JU/N7Y4joJr/23maX\nFy0MmyoaUBvr1PYhAqn8XBa9B1iXzw0TLr3oV01I1CvuSnkY4W8XgarV5OiqyDjT\n9ayWObxc0+MtlDKMaI+8ZAPWVioCxuF3wBy+JZKQOJA3yaihAkEA64pNe2zzO2+g\nuJ2hwZ5P4i8rnfgnO9itioA2vvdqNF89C8xzJukoRtqhnPRQPx/b8qOGsGeFh3Fr\nhysFoIzqwwJBAOFh9nawXJ1bU+pR/2JKwfOx6po5B8ALO8I6iybFUj6bb1htbaFF\njqZNNmCGni32rz30JvFjjRyLrenggJzJzxECQHgGff1LQ5ciBxCMowT7G1HzH5Lc\nBYIlpClTtJITmfceIQmGIZfOcEvK1VgZ11qTbY1zbwstdYnTbivu7Gsn4+kCQQCN\nZuW3b0yb2Pmb8Ff2tgpbN0uF+LPZE/MpF4vIBlJkPyarZvQ6Eya9RYIRK0RAeB1Y\nFD7+gUO+HhA9xIFMXPzRAkEAiqYBs4xrnNsTVvwT2DowQSnmumqVL6XnDgJCMlqH\nAe8bE24Vr87RJnTWq3B+OUj6CGKsSJ8qNu3KBt0xRaNSfQ==\n-----END RSA PRIVATE KEY-----" > /${PRIVATE_KEY_FILE} \
    && echo -e "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDPXrBE8P6svSDu3lb1akbhyHIB\nJ0/1vEQlURE5uTySRRs7wpHI40Oo9R7W9Yx/wcoXKzIOkz5+fjMoZrfwDz8mse5k\naddc08DUXyxjW3k3VujYDPyjSJvp34rdjeTfHog/dPHKmF7vlTb3UO5QdIY6bi5C\nSJlnFearX1dkwkpD8wIDAQAB\n-----END PUBLIC KEY-----" > /${PUBLIC_KEY_FILE}

ENV PYTHONBREAKPOINT=ipdb.set_trace

COPY tests tests

ENTRYPOINT ["pytest", "tests", "--durations=5", "-v", "-l", "--color=yes", "--code-highlight=yes"]
