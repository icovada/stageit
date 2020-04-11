FROM python:3.8-slim as worker-compile
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc
WORKDIR /code

RUN pip install --upgrade pip
ADD requirements.txt .

RUN pip install --user -r requirements.txt

FROM python:3.8-slim as worker-running
WORKDIR /code
COPY --from=worker-compile /root/.local /root/.local

COPY . /code/
ENV PATH=/root/.local/bin:$PATH