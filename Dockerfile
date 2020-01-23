FROM python:3.8
ENV PYTHONUNBUFFERED 1
WORKDIR /code
RUN pip install psycopg2-binary
RUN pip install pipenv
RUN pip install gunicorn
COPY Pipfile .
RUN pipenv install --system --skip-lock
