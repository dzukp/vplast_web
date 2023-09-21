FROM python:3.11-buster

WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY ./requirements.txt .
COPY ./run.sh .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app/ .

#CMD ["./run.sh"]
