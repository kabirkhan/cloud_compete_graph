FROM python:3.6
ENV PORT 8080
EXPOSE ${PORT}
WORKDIR /usr/src

COPY ./requirements.txt .

RUN pip install -r requirements.txt
RUN python -m spacy download en

COPY ./app ./app
COPY ./data ./data

COPY start.sh .
CMD ["bash", "start.sh"]