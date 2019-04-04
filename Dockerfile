FROM python:3.7-alpine
ENV PORT 8080
EXPOSE ${PORT}
WORKDIR /usr

RUN apk add build-base

COPY requirements/api.txt requirements/api.txt
COPY requirements/test.txt requirements/test.txt

RUN pip3 install -r requirements/api.txt
RUN pip3 install -r requirements/test.txt

COPY .env .env
COPY ./src ./src

COPY start.sh .
CMD ["sh", "start.sh"]