FROM python:3.7-alpine
ENV PORT 8080
EXPOSE ${PORT}
WORKDIR /usr

COPY ./requirements/api.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY .env .env
COPY ./src ./src

COPY start.sh .
CMD ["bash", "start.sh"]