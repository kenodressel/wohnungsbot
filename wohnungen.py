import os
import pickle
import bs4
import requests
import hashlib
import telegram
import asyncio
import re
import sys
from pathlib import Path

PICKLE_PATH = './data/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def compare(entries, name):
    Path(PICKLE_PATH).mkdir(parents=True, exist_ok=True)
    hashes = set()
    if(os.path.isfile(PICKLE_PATH + name + '.pickle')):
        with open(PICKLE_PATH + name + '.pickle','rb') as f:
            hashes = pickle.load(f)
    new_entries = [e for e in entries if e['hash'] not in hashes]
    new_hashes = set([e['hash'] for e in new_entries]) | hashes
    with open(PICKLE_PATH + name + '.pickle','wb') as f:
            pickle.dump(new_hashes, f)
    
    return new_entries

def getGerschlauer():
    r = requests.get('https://www.gerschlauer.de/property-search/?location=muenchen&status=zu-vermieten&type=wohnungen', headers=HEADERS)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='infiniteresults')
    entries = lists[0].find_all('div', class_='objekt')
    found_entities = []
    for e in entries:
        preis = e.find('div', class_='preis')
        if not preis or not preis.find('span', class_='miete'):
            continue
        title = e.find('h2')
        if not title:
            continue
        ort = e.find('div', class_='ort')
        if ort and "München" not in ort.text:
            continue
        str_sum = ''
        str_sum += title.text.strip() + '\n'
        str_sum += preis.text.strip() + '\n'
        infos = e.find_all('div', class_='info')
        for info in infos:
            str_sum += info.text.strip() + '\n'
        link_tag = e.find('a', class_='oldobjekt_detail_link') or e.find('a')
        link = 'https://www.gerschlauer.de' + str(link_tag['href'])
        found_entities.append({
            "text": str_sum,
            "link": link,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getAigner():
    data_RAW = {
        "action_form":"ajax_immo_search",
        "auslandImmos":"0",
        "fid":"1931",
        "immoType":"IMMOBILIEN",
        "objekteProSeite":"999",
        "plz":"8",
        "page": "1",
        "validVermarktungsarten":"MIETE_PACHT",
        "auslandImmos":"0",
        "extraAjaxFile": "//modules/pageFramesAndModules/__frames/immoSearchResult/immoSearchResult_004"
    }

    r = requests.post('https://www.mietwohnungsboerse.de/inc/modules/ajax.includes.php', data=data_RAW)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    
    entries = b.find_all('div', class_='immo-box')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('div',class_='immo-desc').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='immo-ort').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='immo-preis-label').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='immo-preis-value').text.strip()) + '\n'
        link = 'https://www.mietwohnungsboerse.de' + str(e.find('a')['href'])
        found_entities.append({
            "text": str_sum,
            "link": link,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getHegerich():
    r = requests.get('https://www.hegerich-immobilien.de/Mietangebote.htm', headers=HEADERS)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='infiniteresults')
    entries = lists[0].find_all('div', class_='objekt')
    found_entities = []
    for e in entries:
        str_sum = ''
        title = e.find('h2')
        if not title:
            continue
        str_sum += title.text.strip() + '\n'
        preis = e.find('div', class_='preis')
        if preis:
            str_sum += preis.text.strip() + '\n'
        infos = e.find_all('div', class_='info')
        for info in infos:
            str_sum += info.text.strip() + '\n'
        link_tag = e.find('h2').find('a')
        link = 'https://www.hegerich-immobilien.de' + str(link_tag['href'])
        ort = e.find('div', class_='ort')
        if ort and "München" not in ort.text:
            continue
        found_entities.append({
            "text": str_sum,
            "link": link,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities
    
def getSchneider():
    r = requests.get('https://www.immobilienschneider.com/mietangebote/')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='oo-listframe')
    entries = lists[0].find_all('div', class_='oo-listobject')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('div',class_='oo-listtitle').text.strip()) + '\n'
        information = [info for info in e.find('div',class_='oo-listinfotable').findAll('div', class_='oo-listtd')]
        for index, info in enumerate(information):
            str_sum += info.text
            str_sum = str_sum + '\n' if (index + 1) % 2 == 0 else str_sum
        link = str(e.find('div',class_='oo-detailslink').find('a', class_='oo-details-btn')['href'])
        if "OBJEKTARTWOHNUNG" not in str_sum.upper().replace(" ", ""):
            continue
        found_entities.append({
            "text": str_sum,
            "link": link,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getRiedel():
    r = requests.get('https://www.riedel-immobilien.de/angebote/wohnungen-mieten', headers=HEADERS)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('ul', class_='listDefault_varImmobox')
    entries = lists[0].find_all('div', class_='listEntryInner')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('h3').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='listEntryLocationShort').text.strip()) + '\n'
        information = str(e.find('div', class_='listEntryObjektdaten').text.strip())
        str_sum += re.sub('\n', '', re.sub(' +', ' ', information)) + '\n'
        if "BÜRO" in str_sum.upper() or "GEWERBE" in str_sum.upper():
            continue
        link = 'https://www.riedel-immobilien.de' + str(e.find('a')['href'])
        found_entities.append({
            "text": str_sum,
            "link": link,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getRogers():
    r = requests.get('https://www.rogers-immobilien.de/immobilien-muenchen/immobilienangebote/')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find('div', class_='et_pb_posts')
    entries = lists.find_all('article', class_='et_pb_post')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('h2',class_='entry-title').text.strip())
        information = str(e.find('div', class_='post-data').text.strip())
        str_sum += re.sub('\n', '', re.sub(' +', ' ', information)) + '\n'
        link = str(e.find('a',class_='et_pb_button')['href'])
        if "KAUFPREIS" not in str_sum.upper() and "ERFOLGREICH VERMITTELT" not in str_sum.upper() and "BÜRO" not in str_sum.upper() and "GEWERBE" not in str_sum.upper():
            found_entities.append({
                "text": str_sum,
                "link": link,
                "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
            })
    return found_entities

dry_run = '--dry-run' in sys.argv

print("Running Script" + (" (dry run)" if dry_run else ""))

all_methods = { "aigner": getAigner, "rogers":getRogers, "riedel":getRiedel, "schneider":getSchneider, "hegerich":getHegerich, "gerschlauer":getGerschlauer}
for name, m in all_methods.items():
    try:
        data = m()
        new_entries = compare(data, name)
        print(f"{name}: {len(data)} total, {len(new_entries)} new")
        if dry_run:
            for e in new_entries:
                print(f"  - {e['text'].splitlines()[0]}")
            continue
        if(len(new_entries) > 0):
            messages = []
            msg_text = 'Neue Ergebnisse von ' + name + '\n\n'
            for e in new_entries:
                entry_text = e['text'] + '\n' + e['link'] + '\n\n'
                if len(msg_text) + len(entry_text) > 4000:
                    messages.append(msg_text)
                    msg_text = 'Neue Ergebnisse von ' + name + ' (Forts.)\n\n'
                msg_text += entry_text
            messages.append(msg_text)

            async def send_all():
                async with telegram.Bot(token=os.environ['TELEGRAM_TOKEN']) as bot:
                    for msg in messages:
                        await bot.send_message(chat_id=os.environ['TELEGRAM_CHAT_ID'], text=msg)

            asyncio.run(send_all())
    except Exception as ex:
        print(f"Error fetching {name}: {ex}")
