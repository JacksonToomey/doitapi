FROM python:3.6

COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock

RUN pip install pipenv

WORKDIR /app

RUN pipenv install

COPY . /app

EXPOSE 8000

CMD ["pipenv run gunicorn app:app"]
