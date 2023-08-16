FROM python:3.10
USER root

WORKDIR problem-solvig
COPY . ./

RUN pip install -r requirements.txt

ENTRYPOINT python main.py