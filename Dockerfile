FROM jfloff/alpine-python:3.6-slim

RUN apk add build-base libffi-dev openssl-dev

COPY cronscript.sh /etc/periodic/15min/wohnungen
RUN pip install bs4 requests python-telegram-bot html5lib

CMD [ "crond", "-l", "2", "-f" ]
