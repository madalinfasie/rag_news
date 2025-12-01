FROM python:3.13-slim
ARG CODE=/code

WORKDIR ${CODE}

COPY . ${CODE}

RUN pip install uv && uv sync

EXPOSE 8080

CMD ["uv", "run", "python", "main.py"]