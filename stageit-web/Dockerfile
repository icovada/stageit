FROM python:3.8-slim as web-compile
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc
WORKDIR /code

RUN pip install --upgrade pip
ADD requirements.txt .

RUN pip install --user -r requirements.txt

FROM python:3.8-slim as web-running
WORKDIR /code
COPY --from=web-compile /root/.local /root/.local

COPY . /code/
COPY entrypoint.sh /usr/src/app/entrypoint.sh
ENV PATH=/root/.local/bin:$PATH