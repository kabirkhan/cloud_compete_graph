FROM python:3.7-slim
ENV PORT 8080
EXPOSE ${PORT}
WORKDIR /usr

# RUN apk add build-base

ADD ./requirements .

RUN pip3 install -r requirements/api.txt
RUN pip3 install -r requirements/test.txt

COPY .env .env
COPY ./src ./src

COPY start.sh .
CMD ["sh", "start.sh"]