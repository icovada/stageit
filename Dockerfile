FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY Pipfile Pipfile.lock /code/
RUN pip install pipenv
RUN pipenv install --system
COPY . /code
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
