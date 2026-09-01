import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import re

sezone = [
    {'url': 'https://www.11v11.com/competitions/premier-league/2026/matches/', 'html_ime': 'sezona_2026.html'},
    {'url': 'https://www.11v11.com/competitions/premier-league/2025/matches/', 'html_ime': 'sezona_2025.html'},

]
strelci_url = [
    {'url': 'https://www.11v11.com/competitions/premier-league/2026/goal-scorers/', 'html_ime': 'strelci_2026.html'},
    {'url': 'https://www.11v11.com/competitions/premier-league/2025/goal-scorers/', 'html_ime': 'strelci_2025.html'},
]

directory = 'podatki'
frontpage_filename = 'glavna.html'
csv_filename = 'tekme.csv'
strelci_csv_filename = 'strelci.csv'

def download_url_to_string(url):
    headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
    }
    try:
        odgovor = requests.get(url, headers=headers)
    except Exception as e:
        print("prišlo je do napake:", e)
        return None
    if odgovor.status_code == 200:
        return odgovor.text
    else:
        print("Status koda:", odgovor.status_code)
        return None
    
def save_string_to_file(text, directory, filename):
    os.makedirs(directory, exist_ok = True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding = 'utf8') as file_out:
        file_out.write(text)
    return None

def save_frontpage(page, directory, filename):
    text = download_url_to_string(page)
    if text is not None:
        if not os.path.exists(directory):
            os.makedirs(directory)
        save_string_to_file(text, directory, filename)
    else:
        print("Podatki niso preneseni")

def read_file_to_string(directory, filename):
    path = os.path.join(directory, filename)
    with open(path, encoding="utf8") as file:
        return file.read()
    
def odstrani_html_znacke(html):
    return re.sub(r'<[^>]+>', '', html)

pozicije_cache = {}  # da vsakega igralca prenesemo samo enkrat, ne za vsak gol/tekmo posebej

def igralci_urls_iz_tekme(html):
    """Iz surovega HTML-ja ene tekme izlušči {ime_igralca: url} iz sestave in klopi."""
    vzorec = r'<a href="(/players/[^"]+)">(.*?)</a>'
    zadetki = re.findall(vzorec, html, re.S)

    slovar = {}
    for pot, ime_html in zadetki:
        ime = odstrani_html_znacke(ime_html).strip()
        url = f"https://www.11v11.com{pot}"
        slovar[ime] = url
    return slovar


def pozicija_igralca(url):
    if url in pozicije_cache:
        return pozicije_cache[url]

    html = download_url_to_string(url)
    if html is None:
        pozicije_cache[url] = ''
        return ''

    text = odstrani_html_znacke(html)
    idx = text.find('Position')
    if idx == -1:
        pozicije_cache[url] = ''
        return ''

    okno = text[idx:idx + 60]
    vzorec_pozicije = r'(Goalkeeper|Defender(?:/[A-Za-z ]+)?|Midfielder(?:/[A-Za-z ]+)?|Forward)'
    rezultat = re.search(vzorec_pozicije, okno)

    pozicija = rezultat.group(1) if rezultat else ''
    pozicije_cache[url] = pozicija
    return pozicija
    
def strelci_tekme_from_url(url):
    html = download_url_to_string(url)

    if html is None:
        return {
            'strelci_domaci': '',
            'strelci_gostje': ''
        }

    igralci_urls = igralci_urls_iz_tekme(html)  # imena -> url, iz sestave/klopi te tekme

    text = odstrani_html_znacke(html)

    rezultat = re.search(r'Goals:(.*?)Starting lineup:', text, re.S)

    if rezultat is None:
        return {
            'strelci_domaci': '',
            'strelci_gostje': ''
        }

    goals_text = rezultat.group(1)

    deli = goals_text.split('Goals:')
    domaci_text = deli[0]
    gostje_text = deli[1] if len(deli) > 1 else ""

    vzorec_gola = r"([A-ZÀ-Ž][A-Za-zÀ-Ž'.\- ]*?)\s+(\d{1,3}(?:\+\d{1,2})?)\b"

    domaci_goli = re.findall(vzorec_gola, domaci_text)
    gostje_goli = re.findall(vzorec_gola, gostje_text)

    def oblikuj(goli):
        vnosi = []
        for ime, minuta in goli:
            ime = ime.strip()
            url_igralca = igralci_urls.get(ime)
            pozicija = pozicija_igralca(url_igralca) if url_igralca else ''
            if pozicija:
                vnosi.append(f"{ime} ({pozicija}) {minuta}'")
            else:
                vnosi.append(f"{ime} {minuta}'")
        return ", ".join(vnosi)

    strelci_domaci = oblikuj(domaci_goli)
    strelci_gostje = oblikuj(gostje_goli)

    return {
        'strelci_domaci': strelci_domaci,
        'strelci_gostje': strelci_gostje
    }



def process_match(zadetek):
    datum, domaca, match_path, goli_domaca, goli_gost, gost = zadetek
    url = f"https://www.11v11.com{match_path}"
    kartoni = kartoni_from_url(url)
    strelci = strelci_tekme_from_url(url)

    return {
        'datum': datum,
        'domaca_ekipa': domaca.strip(),
        'gostujoca_ekipa': gost.strip(),
        'goli_domaca': int(goli_domaca),
        'goli_gost': int(goli_gost),

        'rumeni_domaci': kartoni['rumeni_domaci'],
        'rumeni_gostje': kartoni['rumeni_gostje'],
        'rdeci_domaci': kartoni['rdeci_domaci'],
        'rdeci_gostje': kartoni['rdeci_gostje'],
        'kartoni_domaci': kartoni['kartoni_domaci'],
        'kartoni_gostje': kartoni['kartoni_gostje'],

        'strelci_domaci': strelci['strelci_domaci'],
        'strelci_gostje': strelci['strelci_gostje']
    }

def from_file(directory, filename, sezona):
    html = read_file_to_string(directory, filename)

    vzorec = r'<tr><td>(\d{2} \w{3} \d{4})</td><td class="home">(.*?)</td><td class="score">.*?<a href="(/matches/[^"]+)" title="view match details">(\d+):(\d+)</a></td><td>(.*?)</td>'
    zadetki = re.findall(vzorec, html, re.S)

    data = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(process_match, zadetek)
            for zadetek in zadetki
        ]

        for future in as_completed(futures):
            tekma = future.result()
            print(tekma)      # Printed immediately when this thread finishes
            data.append(tekma)

    return data


def strelci_from_file(directory, filename):
    """Funkcija prebere stran s strelci sezone in vrne seznam slovarjev
    z imenom igralca, ekipo in številom golov."""
    html = read_file_to_string(directory, filename)
    text = odstrani_html_znacke(html)

    vzorec = r'(\d+) goals?\s*([A-ZÀ-ž][A-Za-zÀ-ž\-\' ]+?)\s*\(([A-Za-z &]+?)\)'
    zadetki = re.findall(vzorec, text)

    data = []
    for zadetek in zadetki:
        goli, ime, ekipa = zadetek
        strelec = {
            'ime': ime.strip(),
            'ekipa': ekipa.strip(),
            'goli': int(goli),
        }
        data.append(strelec)

    return data

def kartoni_from_url(url):
    html = download_url_to_string(url)

    if html is None:
        return {
            'rumeni_domaci': 0, 'rumeni_gostje': 0,
            'rdeci_domaci': 0, 'rdeci_gostje': 0,
            'kartoni_domaci': '', 'kartoni_gostje': ''
        }

    text = odstrani_html_znacke(html)

    vzorec = r'Cards:(.*?)(?:On the bench|Comments)'
    rezultat = re.search(vzorec, text, re.S)

    if rezultat is None:
        return {
            'rumeni_domaci': 0, 'rumeni_gostje': 0,
            'rdeci_domaci': 0, 'rdeci_gostje': 0,
            'kartoni_domaci': '', 'kartoni_gostje': ''
        }

    cards_text = rezultat.group(1)
    parts = cards_text.split('Cards:')
    domaci_text = parts[0]
    gostje_text = parts[1] if len(parts) > 1 else ""

    # ime igralca + minuta + tip kartona (Y ali R)
    vzorec_kartona = r"([A-ZÀ-Ž][A-Za-zÀ-Ž'.\- ]*?)\s+(\d{1,3}(?:\+\d{1,2})?)\s*([YR])\b"

    domaci_kartoni = re.findall(vzorec_kartona, domaci_text)
    gostje_kartoni = re.findall(vzorec_kartona, gostje_text)

    def oblikuj(kartoni):
        return ", ".join(f"{ime.strip()} {minuta}' ({tip})" for ime, minuta, tip in kartoni)

    return {
        'rumeni_domaci': len(re.findall(r'\bY\b', domaci_text)),
        'rumeni_gostje': len(re.findall(r'\bY\b', gostje_text)),
        'rdeci_domaci': len(re.findall(r'\bR\b', domaci_text)),
        'rdeci_gostje': len(re.findall(r'\bR\b', gostje_text)),
        'kartoni_domaci': oblikuj(domaci_kartoni),
        'kartoni_gostje': oblikuj(gostje_kartoni)
    }

def write_csv(fieldnames, rows, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding = 'utf8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return


def write_matches_to_csv(ads, directory, filename):
    assert ads and (all(j.keys() == ads[0].keys() for j in ads))
    fieldnames = sorted(ads[0].keys())
    write_csv(fieldnames, ads, directory, filename)


def main(redownload = True, reparse = True):
    vse_tekme = []
    vsi_strelci = []

    for sezona in sezone:
        path_html_file = os.path.join(directory, sezona['html_ime'])


        if not os.path.exists(path_html_file):
            save_frontpage(sezona['url'], directory, sezona['html_ime'])


        tekme = from_file(directory, sezona['html_ime'], sezona)
        vse_tekme.extend(tekme)


    write_matches_to_csv(vse_tekme, directory, csv_filename)


    for sezona in strelci_url:
        path_html_file = os.path.join(directory, sezona['html_ime'])


        if not os.path.exists(path_html_file):
            save_frontpage(sezona['url'], directory, sezona['html_ime'])


        strelci = strelci_from_file(directory, sezona['html_ime'])
        vsi_strelci.extend(strelci)

    write_matches_to_csv(vsi_strelci, directory, strelci_csv_filename)

    print(f"Shranjenih {len(vse_tekme)} tekem in {len(vsi_strelci)} strelcev.")

   


if __name__ == '__main__':
    main()



        
