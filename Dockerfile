FROM python:3.10-slim

LABEL org.opencontainers.image.authors="bpetit@hubblo.org"

RUN apt update && apt install lshw nvme-cli -y

RUN useradd -ms /bin/bash boagent

WORKDIR /home/boagent

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ENV PATH $PATH:/home/boagent/.local/bin

COPY . .

EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "-c", "uvicorn --reload boagent.api.api:app --host 0.0.0.0" ]
