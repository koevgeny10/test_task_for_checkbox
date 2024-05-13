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

ENV PYTHONBREAKPOINT=ipdb.set_trace
ENV DEBUG=0

COPY tests tests

ENTRYPOINT ["pytest", "tests", "--durations=5", "-v", "-l", "--color=yes", "--code-highlight=yes"]
