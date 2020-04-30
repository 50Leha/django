FROM python:3.6
RUN apt-get update && apt-get install -y locales locales-all
WORKDIR /code
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./
RUN python manage.py migrate
CMD python manage.py runserver 0.0.0.0:8080