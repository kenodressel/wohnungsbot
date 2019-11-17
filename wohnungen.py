import os.path
import pickle
import bs4
import requests
import hashlib
import telegram

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
    r = requests.get('http://site20.elviraimmobiliengmbh.netcore.web2.onoffice.de/mietobjekte.xhtml')
    b = bs4.BeautifulSoup(r.text, "html5lib")
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
    page = 1
    total_results = []
    data_RAW = {
        "action_form":"ajax_immo_search",
        "auslandImmos":"0",
        "extraAjaxFile":"/modules/pageFramesAndModules/__frames/custom/immoSearchResult_2018",
        "fid":"5998",
        "immoType":"IMMOBILIEN",
        "objektart":"WOHNUNG",
        "objekteProSeite":"50",
        "page":str(page),
        "region":"DB+O+CG+",
        "vermarktungsart":"MIETE_PACHT"
    }

    r = requests.post('https://www.aigner-immobilien.de/inc/modules/ajax.includes.php', data=data_RAW, verify=False)
    results = r.json()['mapData']
    total_results += results
    found_entities = []
    for entry in total_results:
        str_sum = ''
        str_sum += str(entry['flaeche']['value']) + '\n'
        str_sum += str(entry['iconData']['schlafen']) + '-Zimmer' + '\n'
        str_sum += str(entry['location']) + '\n'
        str_sum += str(entry['preis']['original']) + str(entry['preis']['text']) + '\n'
        found_entities.append({
            "text": str_sum,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getGerschlauer():
    r = requests.get('https://www.gerschlauer.de/property-search/?location=muenchen&status=zu-vermieten&type=wohnungen', verify=False)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='property-items-container')
    entries = lists[0].find_all('div', class_='span6')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('h4').text.strip()) + '\n'
        str_sum += str(e.find('h5',class_='price').text.strip()) + '\n'
        found_entities.append({
            "text": str_sum,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getHegerich():
    r = requests.get('https://www.hegerich-immobilien.de/Mietangebote.htm', verify=False)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='infiniteresults')
    entries = lists[0].find_all('div', class_='objekt')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('h3').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='preis').text.strip()) + '\n'
        infos = e.find_all('div', class_='info')
        if(len(infos) > 0):
            str_sum += str(infos[0].text.strip()) + '\n'
            str_sum += str(infos[1].text.strip()) + '\n'
        found_entities.append({
            "text": str_sum,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities
    
def getSchneider():
    r = requests.get('https://www.immobilienschneider.com/aktuelle-angebote/wohnung-muenchen-miete', verify=False)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='je-items-item-box')
    entries = lists[0].find_all('div', class_='data-cd-grid-match')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('a',class_='je-items-item-title').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='je-items-price').text.strip()) + '\n'
        if(len(e.find_all('span', class_='cd-customfield-value')) > 0):
            str_sum += str(e.find_all('span', class_='cd-customfield-value')[0].text) + '\n'
            str_sum += str(e.find_all('span', class_='cd-customfield-value')[1].text) + '\n'
        found_entities.append({
            "text": str_sum,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getRiedel():
    r = requests.get('https://www.riedel-immobilien.de/angebote/wohnungen/?mt=67555823520346', verify=False)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find_all('div', class_='elementList')
    entries = lists[0].find_all('div', class_='listEntryContent')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('div',class_='listEntryHeadline').text.strip()) + '\n'
        str_sum += str(e.find('div',class_='listEntryRegion').text.strip()) + '\n'
        str_sum += str(e.find_all('div', class_='objektDataValue')[1].text) + '\n'
        str_sum += str(e.find_all('div', class_='objektDataValue')[2].text) + '\n'
        found_entities.append({
            "text": str_sum,
            "hash": hashlib.sha1(str.encode(str_sum)).hexdigest()
        })
    return found_entities

def getRogers():
    page = 1
    total_results = []
    data_RAW = {
        "action":"extra_blog_feed_get_content",
        "blog_feed_module_type":"standard",
        "blog_feed_nonce":"7d37f707ea",
        "categories":"5",
        "content_length":"excerpt",
        "date_format":"M+j,+Y",
        "et_load_builder_modules":"1",
        "posts_per_page":"20",
        "to_page":"1",
        "vermarktungsart":"MIETE_PACHT"
    }

    r = requests.post('https://www.rogers-immobilien.de/wp-admin/admin-ajax.php', data=data_RAW, verify=False)
    b = bs4.BeautifulSoup(r.text, "html5lib")
    lists = b.find('div', class_='paginated_page')
    entries = lists.find_all('article', class_='post')
    found_entities = []
    for e in entries:
        str_sum = ''
        str_sum += str(e.find('div',class_='entry-summary').text.strip())
        found_entities.append({
            "text": str_sum,
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
            bot = telegram.Bot(token='526846149:AAFNiHNpFim5oo8U47mx9SZiI-Ei1DIgcQA')
            msg_text = 'Neue Ergebnisse von ' + name + '\n\n'
            for e in new_entries:
                msg_text += e['text'] + '\n\n'

            bot.send_message(chat_id='-297159408',text=msg_text);
    except:
        print("could not fetch data from " + name)
