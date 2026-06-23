FROM python:3.13-slim-bookworm

RUN mkdir -p /usr/src/author-api-republish-mock
WORKDIR /usr/src/author-api-republish-mock

COPY main.py poetry.lock pyproject.toml README.md /usr/src/author-api-republish-mock/

RUN pip install --no-cache-dir poetry==2.1.2 && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

RUN groupadd -r appuser && useradd -r -g appuser -u 999 -m appuser && \
    chown -R appuser:appuser /usr/src

USER appuser

EXPOSE 8081

CMD ["python", "main.py"]
