FROM python:3.10-slim

LABEL org.opencontainers.image.authors="bpetit@hubblo.org"

WORKDIR /home/boagent

RUN python3 -m pip install --upgrade poetry

RUN apt update && apt install lshw nvme-cli -y

COPY pyproject.toml .

RUN poetry install

COPY . .

EXPOSE 8000

ENTRYPOINT ["poetry", "run", "uvicorn", "--reload", "boagent.api.api:app", "--host", "0.0.0.0"]
