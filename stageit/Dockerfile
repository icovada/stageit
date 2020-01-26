FROM python:3.8
ENV PYTHONUNBUFFERED 1
WORKDIR /code
ADD requirements.txt .
RUN pip install -r requirements.txt
COPY . /code/
