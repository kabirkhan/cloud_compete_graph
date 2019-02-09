FROM python:3.6
ENV PORT 8080
EXPOSE ${PORT}
WORKDIR /usr

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY .env .env
COPY ./src ./src

COPY start.sh .
CMD ["bash", "start.sh"]