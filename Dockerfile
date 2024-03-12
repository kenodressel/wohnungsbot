FROM python:slim

# setup cron
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive \
    apt-get install --no-install-recommends --assume-yes \
      cron

RUN echo '* * * * * /root/cronscript.sh > /proc/1/fd/1 2>/proc/1/fd/2' | crontab

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY cronscript.sh /root/cronscript.sh
COPY wohnungen.py /root/wohnungen.py

CMD [ "cron", "-l", "2", "-f" ]
