import csv
import os
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
    
def from_file(directory,filename):
    html = read_file_to_string(directory, filename)
    text = re.sub(r'<[^>]+>', '', html)
    vzorec = r'(\d{2} \w{3} \d{4})([A-Za-z &]+?)(\d+):(\d+)([A-Za-z &]+?)(?=\d{2} \w{3} \d{4}|$)'
    zadetki = re.findall(vzorec, text)
    
    data = []

    for zadetek in zadetki:
        datum, domaca, goli_domaca, goli_gost, gost = zadetek
        kartoni = kartoni_from_url(url)
        tekma = {
            'datum': datum,
            'domaca_ekipa' : domaca.strip(),
            'gostujoca_ekipa': gost.strip(),
            'goli_domaca': int(goli_domaca),
            'goli_gost': int(goli_gost),


            'rumeni_domaci': kartoni['rumeni_domaci'],
            'rumeni_gostje': kartoni['rumeni_gostje'],
            'rdeci_domaci': kartoni['rdeci_domaci'],
            'rdeci_gostje': kartoni['rdece_gostje']
        }
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
        return None
    
    text = odstrani_html_znacke(html)

    vzorec = r'Cards:(.*?)(?:On the bench|Comments)'
    rezultat = re.search(vzorec, text, re.S)

    if rezultat is None:
        return {
            'rumeni_domaci': 0,
            'rumeni_gostje': 0,
            'rdeci_domaci': 0,
            'rdeci_gostje': 0
        }
    
    cards = rezultat.group(1)
    ekipe = cards.split('Cards:')

    return {
        'rumeni_domaci': cards[:len(cards)//2].count('Y'),
        'rumeni_gostje': cards[len(cards)//2:].count('Y'),
        'rdeci_domaci': cards[:len(cards)//2].count('R'),
        'rdeci_gostje': cards[len(cards)//2:].count('R')
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
    fieldnames =sorted(ads[0].keys())
    write_csv(fieldnames, ads, directory, filename)

def main(redownload = True, reparse = True):
    vse_tekme = []
    vsi_strelci = []

    for sezona in sezone:
        path_html_file = os.path.join(directory, sezona['html_ime'])


        if not os.path.exists(path_html_file):
            save_frontpage(sezona['url'], directory, sezona['html_ime'])

    
        tekme = from_file(directory,sezona['html_ime'])
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



        
