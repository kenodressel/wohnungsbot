import os
import pickle
import bs4
import requests
import hashlib
import telegram
import re
import sys

def compare(entries, name):
    hashes = set()
    if(os.path.isfile('./' + name + '.pickle')):
        with open('./' + name + '.pickle','rb') as f:
            hashes = pickle.load(f)
    new_entries = [e for e in entries if e['hash'] not in hashes]
    new_hashes = set([e['hash'] for e in new_entries]) | hashes
    with open('./' + name + '.pickle','wb') as f:
            pickle.dump(new_hashes, f)
    
    return new_entries

def getElvira():
    return []# currently broken
    r = requests.post('http://site20.elviraimmobiliengmbh.netcore.web2.onoffice.de/mietobjekte.xhtml')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    print(r.text)
    return
    lists = b.find_all('div', class_='full')
    entries = lists[1].find_all('div', class_='object-object')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('p',class_='hd').text.strip()) + '\n'
        infos = e.find_all('li')
        if(len(infos) > 0):
            str_sum += str(infos[0].text.strip()) + '\n'
            str_sum += str(infos[1].text.strip()) + '\n'
            str_sum += str(infos[2].text.strip()) + '\n'
        found_entities.append({
            "text": str_sum,
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

def getGerschlauer():
    r = requests.get('https://www.gerschlauer.de/property-search/?location=muenchen&status=zu-vermieten&type=wohnungen')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='list-container')
    entries = lists[0].find_all('article', class_='property-item')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('h4').text.strip()) + '\n'
        str_sum += str(e.find('h5',class_='price').text.strip()) + '\n'
        str_sum += str(e.find('span',class_='property-meta-size').text.strip()) + '\n'
        str_sum = re.sub('\xa0', '', str_sum)
        link = str(e.find('a',class_='more-details')['href'])
        found_entities.append({
            "text": str_sum,
            "link": link,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getHegerich():
    r = requests.get('https://www.hegerich-immobilien.de/Mietangebote.htm')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='infiniteresults')
    entries = lists[0].find_all('div', class_='objekt')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('h3').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='preis').text.strip()) + '\n'
        infos = e.find_all('div', class_='info')
        link = 'https://www.hegerich-immobilien.de' + str(e.find('h3').find('a')['href'])
        if(len(infos) > 0):
            str_sum += str(infos[0].text.strip()) + '\n'
            str_sum += str(infos[1].text.strip()) + '\n'
        if "München" in str(e.find('div',class_='ort').text.strip()):
            found_entities.append({
                "text": str_sum,
                "link": link,
                "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
            })
    return found_entities
    
def getSchneider():
    r = requests.get('https://www.immobilienschneider.com/aktuelle-angebote/wohnung-muenchen-miete')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='jomestate')
    entries = lists[0].find_all('div', class_='card')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('h3').text.strip()) + '\n'
        str_sum += str(e.find('address').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='price').text.strip()) + '\n'
        link = 'https://www.immobilienschneider.com/' + str(e.find('h3').find('a')['href'])
        found_entities.append({
            "text": str_sum,
            "link": link,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getRiedel():
    r = requests.get('https://www.riedel-immobilien.de/angebote?field_marketing_type_value[RENT]=RENT')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='property-search-result')
    entries = lists[0].find_all('div', class_='property-item')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('h3').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='location').find('span').text.strip()) + '\n'
        information = str(e.find('div', class_='information').text.strip())
        str_sum += re.sub('\n', '', re.sub(' +', ' ', information)) + '\n'
        link = 'https://www.riedel-immobilien.de/' + str(e.find('a')['href'])
        found_entities.append({
            "text": str_sum,
            "link": link,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getRogers():
    r = requests.get('https://www.rogers-immobilien.de/immobilien-muenchen/immobilienangebote/')
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find('div', class_='paginated_page')
    entries = lists.find_all('article', class_='post')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('div',class_='entry-summary').text.strip())
        link = str(e.find('a',class_='read-more-button')['href'])
        if "KAUFPREIS" not in str_sum and "ERFOLGREICH VERMITTELT" not in str_sum:
            found_entities.append({
                "text": str_sum,
                "link": link,
                "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
            })
    return found_entities

print("Running Script")

all_methods = { "aigner": getAigner, "rogers":getRogers, "riedel":getRiedel, "schneider":getSchneider, "hegerich":getHegerich, "gerschlauer":getGerschlauer, "elvira":getElvira};
for name, m in all_methods.items():
    try:
        data = m();
        new_entries = compare(data, name)
        print(new_entries)
        if(len(new_entries) > 0):
            bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
            msg_text = 'Neue Ergebnisse von ' + name + '\n\n'
            for e in new_entries:
                msg_text += e['text'] + '\n' + e['link'] + '\n\n'

            bot.send_message(chat_id=os.environ['TELEGRAM_CHAT_ID'],text=msg_text);
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print("could not fetch data from " + name)
