FROM python:3.13-slim

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY wohnungen.py /root/wohnungen.py

WORKDIR /root

CMD [ "python", "-u", "wohnungen.py" ]
