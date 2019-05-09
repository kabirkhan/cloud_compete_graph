FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY requirements/api.txt requirements/api.txt
COPY requirements/test.txt requirements/test.txt

RUN pip3 install -r requirements/api.txt
RUN pip3 install -r requirements/test.txt

ENV PORT 8080
ENV APP_MODULE src.app.api:app
ENV WEB_CONCURRENCY 2
ENV GUNICORN_CONF /app/src/gunicorn_conf.py
COPY .env .env
COPY ./src /app/src
COPY gunicorn_conf.py /app/src/gunicorn_conf.py
COPY start.sh /app

CMD ["bash", "start.sh"]