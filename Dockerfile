FROM python:slim

# RUN apk add build-base libffi-dev openssl-dev

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY cronscript.sh /etc/periodic/15min/wohnungen
COPY wohnungen.py /root/wohnungen.py

CMD [ "crond", "-l", "2", "-f" ]
