FROM python:3.13-slim
ARG CODE=/code

WORKDIR ${CODE}

COPY . ${CODE}

RUN pip install uv && uv sync

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]