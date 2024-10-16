FROM python:3.10-slim

LABEL org.opencontainers.image.authors="open-source@boavizta.org"
LABEL org.opencontainers.image.description="Docker image for Boagent, a local API & environmental impact monitoring tool."
LABEL org.opencontainers.image.licenses=Apache-2.0

WORKDIR /home/boagent

RUN python3 -m pip install --upgrade poetry

RUN apt update && apt install lshw nvme-cli -y

COPY pyproject.toml .

RUN poetry install

COPY . .

EXPOSE 8000

ENTRYPOINT ["poetry", "run", "uvicorn", "--reload", "boagent.api.api:app", "--host", "0.0.0.0"]
