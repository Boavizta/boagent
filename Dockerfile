FROM python:3.10-slim

LABEL org.opencontainers.image.authors="bpetit@hubblo.org"

RUN apt update && apt install gcc g++ -y

RUN apt-get install -y cron sqlite3

RUN useradd -ms /bin/bash boagent

#USER boagent

WORKDIR /home/boagent

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ENV PATH $PATH:/home/boagent/.local/bin

WORKDIR /home/boagent/db

RUN sqlite3 boagent.db

WORKDIR /home/boagent

COPY . .

EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "-c", "cd boagent/api && uvicorn --reload api:app --host 0.0.0.0" ]
