FROM python:3

RUN mkdir -p /etl/tmp
RUN mkdir -p /usr/src/app
COPY /files /etl

COPY app /usr/src/app/
WORKDIR /usr/src/app/

RUN python -m pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install pymongo

EXPOSE 8080

CMD cd src && gunicorn wsgi:app --config=config.py