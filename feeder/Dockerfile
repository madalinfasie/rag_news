FROM python:3.13-slim
ARG CODE=/code

WORKDIR ${CODE}

COPY . ${CODE}

RUN pip install uv && uv sync
RUN apt update -y && apt install -y cron

RUN crontab ${CODE}/crontab

CMD cron && tail -f /dev/null
