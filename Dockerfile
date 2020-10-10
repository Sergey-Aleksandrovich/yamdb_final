FROM python:3.8.5

WORKDIR /code

COPY requirements.txt /code

RUN pip install -r /code/requirements.txt

CMD python manage.py collectstatic

COPY . /code
