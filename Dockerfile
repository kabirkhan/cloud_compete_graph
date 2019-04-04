FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
# ENV PORT 8080
# EXPOSE ${PORT}
ENV APP_MODULE src.app.api:app

# RUN apk add build-base

COPY requirements/api.txt requirements/api.txt
COPY requirements/test.txt requirements/test.txt

RUN pip3 install -r requirements/api.txt
RUN pip3 install -r requirements/test.txt

COPY .env .env
COPY ./src /app/src

# COPY start.sh .
# CMD ["sh", "start.sh"]