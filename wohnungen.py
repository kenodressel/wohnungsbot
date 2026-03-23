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

def entry(title, link, price=None, location=None, size=None, rooms=None):
    return {
        "title": title.strip(),
        "price": price.strip() if price else None,
        "location": location.strip() if location else None,
        "size": size.strip() if size else None,
        "rooms": rooms.strip() if rooms else None,
        "link": link.strip(),
        "id": hashlib.sha1(link.strip().encode()).hexdigest()
    }

def format_entry(e):
    parts = []
    if e.get('location'):
        parts.append(e['location'])
    if e.get('price'):
        parts.append(e['price'])
    if e.get('size'):
        parts.append(e['size'])
    if e.get('rooms'):
        parts.append(e['rooms'])
    details = ' · '.join(parts)
    lines = [f"<b>{e['title']}</b>"]
    if details:
        lines.append(details)
    lines.append(f"<a href=\"{e['link']}\">→ Exposé</a>")
    return '\n'.join(lines)

def compare(entries, name):
    Path(PICKLE_PATH).mkdir(parents=True, exist_ok=True)
    hashes = set()
    if(os.path.isfile(PICKLE_PATH + name + '.pickle')):
        with open(PICKLE_PATH + name + '.pickle','rb') as f:
            hashes = pickle.load(f)
    new_entries = [e for e in entries if e['id'] not in hashes]
    return new_entries

def save_hashes(entries, name):
    Path(PICKLE_PATH).mkdir(parents=True, exist_ok=True)
    hashes = set()
    if(os.path.isfile(PICKLE_PATH + name + '.pickle')):
        with open(PICKLE_PATH + name + '.pickle','rb') as f:
            hashes = pickle.load(f)
    hashes.update(e['id'] for e in entries)
    with open(PICKLE_PATH + name + '.pickle','wb') as f:
            pickle.dump(hashes, f)

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
    found = []
    for e in b.find_all('div', class_='immo-box'):
        found.append(entry(
            title=e.find('div', class_='immo-desc').text,
            location=e.find('div', class_='immo-ort').text,
            price=e.find('div', class_='immo-preis-value').text,
            size=e.find('div', class_='immo-preis-label').text,
            link='https://www.mietwohnungsboerse.de' + e.find('a')['href']
        ))
    return found

def getRogers():
    r = requests.get('https://www.rogers-immobilien.de/immobilien-muenchen/immobilienangebote/')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    posts = b.find('div', class_='et_pb_posts')
    found = []
    for e in posts.find_all('article', class_='et_pb_post'):
        title = e.find('h2', class_='entry-title').text.strip()
        info = re.sub(r'\s+', ' ', e.find('div', class_='post-data').text).strip()
        link = e.find('a', class_='et_pb_button')['href']
        text = (title + ' ' + info).upper()
        if any(x in text for x in ['KAUFPREIS', 'ERFOLGREICH VERMITTELT', 'BÜRO', 'GEWERBE']):
            continue
        found.append(entry(title=title, link=link))
    return found

def getRiedel():
    r = requests.get('https://www.riedel-immobilien.de/angebote/wohnungen-mieten', headers=HEADERS)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('ul', class_='listDefault_varImmobox')
    found = []
    for e in lists[0].find_all('div', class_='listEntryInner'):
        title = e.find('h3').text.strip()
        location = e.find('div', class_='listEntryLocationShort').text.strip()
        details = re.sub(r'\s+', ' ', e.find('div', class_='listEntryObjektdaten').text).strip()
        if any(x in (title + details).upper() for x in ['BÜRO', 'GEWERBE']):
            continue
        link = 'https://www.riedel-immobilien.de' + e.find('a')['href']
        found.append(entry(title=title, location=location, price=details, link=link))
    return found

def getSchneider():
    r = requests.get('https://www.immobilienschneider.com/mietangebote/')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='oo-listframe')
    found = []
    for e in lists[0].find_all('div', class_='oo-listobject'):
        title = e.find('div', class_='oo-listtitle').text.strip()
        infos = e.find('div', class_='oo-listinfotable').find_all('div', class_='oo-listtd')
        info_pairs = {}
        for i in range(0, len(infos) - 1, 2):
            key = infos[i].text.strip()
            val = infos[i+1].text.strip()
            info_pairs[key] = val
        if info_pairs.get('Objektart', '').upper() != 'WOHNUNG':
            continue
        link = e.find('div', class_='oo-detailslink').find('a', class_='oo-details-btn')['href']
        found.append(entry(
            title=title,
            location=f"{info_pairs.get('PLZ', '')} {info_pairs.get('Ort', '')}".strip(),
            price=info_pairs.get('Kaltmiete') or info_pairs.get('Warmmiete'),
            size=info_pairs.get('Wohnfläche'),
            rooms=info_pairs.get('Anzahl Zimmer', '') + ' Zi.' if info_pairs.get('Anzahl Zimmer') else None,
            link=link
        ))
    return found

def getHegerich():
    r = requests.get('https://www.hegerich-immobilien.de/Mietangebote.htm', headers=HEADERS)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='infiniteresults')
    found = []
    for e in lists[0].find_all('div', class_='objekt'):
        title_tag = e.find('h2')
        if not title_tag:
            continue
        ort = e.find('div', class_='ort')
        if ort and "München" not in ort.text:
            continue
        title = title_tag.text.strip()
        preis = e.find('div', class_='preis')
        infos = e.find_all('div', class_='info')
        size_b = infos[0].find('b') if len(infos) > 0 else None
        rooms_b = infos[1].find('b') if len(infos) > 1 else None
        link = 'https://www.hegerich-immobilien.de' + title_tag.find('a')['href']
        found.append(entry(
            title=title,
            location='München',
            price=preis.text.strip() if preis else None,
            size=size_b.text.strip() if size_b else None,
            rooms=(rooms_b.text.strip() + ' Zi.') if rooms_b else None,
            link=link
        ))
    return found

def getGerschlauer():
    r = requests.get('https://www.gerschlauer.de/property-search/?location=muenchen&status=zu-vermieten&type=wohnungen', headers=HEADERS)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='infiniteresults')
    found = []
    for e in lists[0].find_all('div', class_='objekt'):
        preis = e.find('div', class_='preis')
        if not preis or not preis.find('span', class_='miete'):
            continue
        title_tag = e.find('h2')
        if not title_tag:
            continue
        ort = e.find('div', class_='ort')
        if ort and "München" not in ort.text:
            continue
        infos = e.find_all('div', class_='info')
        size_b = infos[0].find('b') if len(infos) > 0 else None
        rooms_b = infos[1].find('b') if len(infos) > 1 else None
        link_tag = e.find('a', class_='oldobjekt_detail_link') or e.find('a')
        found.append(entry(
            title=title_tag.text.strip(),
            location='München',
            price=preis.text.strip(),
            size=size_b.text.strip() if size_b else None,
            rooms=(rooms_b.text.strip() + ' Zi.') if rooms_b else None,
            link='https://www.gerschlauer.de' + link_tag['href']
        ))
    return found

def getAlsaol():
    r = requests.get('https://www.alsaol.de/aktuelle-immobilienangebote/miete/', headers=HEADERS)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    found = []
    for e in b.select('div.item-wrap'):
        if e.select_one('span.property-status'):
            continue
        title_tag = e.select_one('.item-title a')
        if not title_tag:
            continue
        objektart = e.select_one('p.objektart')
        if objektart and any(x in objektart.text.upper() for x in ['BÜRO', 'GEWERBE', 'PRAXIS', 'LADEN', 'VERKAUF']):
            continue
        location = e.select_one('address.item-address')
        amenities = {}
        for li in e.select('.info-row li'):
            label = li.find('strong')
            val = li.find('span')
            if label and val:
                amenities[label.text.strip()] = val.text.strip()
        rooms = amenities.get('Zimmer', '') + ' Zi.' if amenities.get('Zimmer') else None
        found.append(entry(
            title=title_tag.text.strip(),
            location=location.text.strip() if location else None,
            price=amenities.get('Mietpreis'),
            size=amenities.get('Wohnfläche'),
            rooms=rooms,
            link=title_tag['href']
        ))
    return found

def getWsb():
    found = []
    r = requests.get('https://wsb-bayern.de/immobilien/?vermarktungsart=miete&ort=M%C3%BCnchen', headers=HEADERS)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    for e in b.select('div.property-container'):
            title_tag = e.select_one('h3.property-title a')
            if not title_tag:
                continue
            details = {}
            for row in e.select('div.property-details div.row'):
                text = row.text.strip()
                if ':' in text:
                    k, v = text.split(':', 1)
                    details[k.strip()] = v.strip()
            found.append(entry(
                title=title_tag.text.strip(),
                location=e.select_one('div.property-subtitle').text.strip() if e.select_one('div.property-subtitle') else None,
                price=details.get('Kaltmiete'),
                size=details.get('Wohnfläche ca.') or details.get('Wohnflache ca.'),
                rooms=details.get('Zimmer', '') + ' Zi.' if details.get('Zimmer') else None,
                link=title_tag['href']
            ))
    return found

# --- Main ---

if __name__ != '__main__':
    raise SystemExit

dry_run = '--dry-run' in sys.argv
seed = '--seed' in sys.argv

mode = " (dry run)" if dry_run else " (seed)" if seed else ""
print(f"Running Script{mode}")

all_methods = {
    "Aigner": getAigner,
    "Rogers": getRogers,
    "Riedel": getRiedel,
    "Schneider": getSchneider,
    "Hegerich": getHegerich,
    "Gerschlauer": getGerschlauer,
    "ALSAOL": getAlsaol,
    "WSB Bayern": getWsb,
}
seed_errors = False
for name, m in all_methods.items():
    try:
        data = m()
        if seed:
            save_hashes(data, name)
            print(f"{name}: seeded {len(data)} entries")
            continue
        new_entries = compare(data, name)
        print(f"{name}: {len(data)} total, {len(new_entries)} new")
        if dry_run:
            for e in new_entries:
                print(f"  - {e['title']}")
            continue
        if len(new_entries) > 0:
            messages = []
            header = f"<b>Neue Mietwohnungen von {name}</b>\n"
            msg_text = header + '\n'
            for e in new_entries:
                entry_text = format_entry(e) + '\n\n'
                if len(msg_text) + len(entry_text) > 4000:
                    messages.append(msg_text)
                    msg_text = header + ' (Forts.)\n\n'
                msg_text += entry_text
            messages.append(msg_text)

            async def send_all(msgs=messages):
                async with telegram.Bot(token=os.environ['TELEGRAM_TOKEN']) as bot:
                    for msg in msgs:
                        await bot.send_message(
                            chat_id=os.environ['TELEGRAM_CHAT_ID'],
                            text=msg,
                            parse_mode='HTML',
                            disable_web_page_preview=True
                        )

            asyncio.run(send_all())
        save_hashes(data, name)
    except Exception as ex:
        print(f"Error fetching {name}: {ex}")
        if seed:
            seed_errors = True

if seed and seed_errors:
    print("Seed completed with errors.")
    sys.exit(1)
