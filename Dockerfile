FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY Pipfile /code/
RUN pip install psycopg2-binary
RUN pip install pipenv
RUN pipenv install --system --skip-lock
COPY . /code
