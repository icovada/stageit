FROM debian
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY Pipfile Pipfile.lock /code/
RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install python3-pip -y
RUN pip3 install pipenv
RUN pipenv install --system
COPY . /code
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]