import csv
import os
import requests
import re

###############################################################################
# Najprej definirajmo nekaj pomožnih orodij za pridobivanje podatkov s spleta.
###############################################################################

# definirajte URL glavne strani bolhe za oglase z mačkami
frontpage_url = 'https://www.worldfootball.net/competition/co91/england-premier-league/se74714/2024-2025/all-matches/'
# mapa, v katero bomo shranili podatke
directory = 'podatki'
# ime datoteke v katero bomo shranili glavno stran
frontpage_filename = 'glavna.html'
# ime CSV datoteke v katero bomo shranili podatke
csv_filename = 'tekme.csv'


def download_url_to_string(url):
    """Funkcija kot argument sprejme niz in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
    }
    try:
        # del kode, ki morda sproži napako
        odgovor = requests.get(url, headers=headers)
    except Exception as e:
        # koda, ki se izvede pri napaki
        # dovolj je če izpišemo opozorilo in prekinemo izvajanje funkcije
        print("Prišlo je do napake:", e)
        return None
    # nadaljujemo s kodo če ni prišlo do napake
    if odgovor.status_code == 200:
        return odgovor.text
    else:
        print("Status koda:", odgovor.status_code)
        return None



def save_string_to_file(text, directory, filename):
    """Funkcija zapiše vrednost parametra "text" v novo ustvarjeno datoteko
    locirano v "directory"/"filename", ali povozi obstoječo. V primeru, da je
    niz "directory" prazen datoteko ustvari v trenutni mapi.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None


# Definirajte funkcijo, ki prenese glavno stran in jo shrani v datoteko.


def save_frontpage(page, directory, filename):
    """Funkcija shrani vsebino spletne strani na naslovu "page" v datoteko
    "directory"/"filename"."""
    tekst = download_url_to_string(page)
    if tekst is not None:
        save_string_to_file(tekst, directory, filename)
    else:
        print("Podatki niso prenešeni.")


###############################################################################
# Po pridobitvi podatkov jih želimo obdelati.
###############################################################################


def read_file_to_string(directory, filename):
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz."""
    path = os.path.join(directory, filename)
    with open(path, encoding="utf8") as file:
        return file.read()


# Definirajte funkcijo, ki sprejme niz, ki predstavlja vsebino spletne strani,
# in ga razdeli na dele, kjer vsak del predstavlja en oglas. To storite s
# pomočjo regularnih izrazov, ki označujejo začetek in konec posameznega
# oglasa. Funkcija naj vrne seznam nizov.


def page_to_ads(page_content):
    """Funkcija poišče posamezne oglase, ki se nahajajo v spletni strani in
    vrne seznam oglasov."""
    # .+? zagotovi, da ujame do prvega konca article in ne gre do zadnjega
    vzorec = r"<article.+?href=\"/macke.+?</article>"
    #flags... isce cez vec vrstic, ne sam eno!
    return re.findall(vzorec, page_content, flags=re.DOTALL)


# Definirajte funkcijo, ki sprejme niz, ki predstavlja oglas, in izlušči
# podatke o imenu, lokaciji, datumu objave in ceni v oglasu.


def get_dict_from_ad_block(block):
    """Funkcija iz niza za posamezen oglasni blok izlušči podatke o imenu, ceni
    in opisu ter vrne slovar, ki vsebuje ustrezne podatke."""
    ime_vzorec = r'<h3 class="entity-title".+?<span>(.+?)<.span>'
    cena_vzorec = r'<strong.+?>(.+?)<.strong>'
    datum_vzorec = r'<time.+?>(.+?)<.time>'
    try:
        ime = re.search(ime_vzorec, block).group(1)
        cena = re.search(cena_vzorec, block).group(1)
        datum = re.search(datum_vzorec, block).group(1)
    except AttributeError:
        print('Napačna struktura oglasa')
        return None

    return {'ime': ime, 'cena': cena, 'datum': datum}


# Definirajte funkcijo, ki sprejme ime in lokacijo datoteke, ki vsebuje
# besedilo spletne strani, in vrne seznam slovarjev, ki vsebujejo podatke o
# vseh oglasih strani.


def ads_from_file(filename, directory):
    """Funkcija prebere podatke v datoteki "directory"/"filename" in jih
    pretvori (razčleni) v pripadajoč seznam slovarjev za vsak oglas posebej."""
    #preberemo podatke iz datoteke
    text = read_file_to_string(directory, filename)
    #izluščimo oglase
    ads = page_to_ads(text)
    #vsak oglas pretvorimo v slovar podatkov
    data = []
    for ad in ads:
        #dobimo podatke
        ad_data = get_dict_from_ad_block(ad)
        if ad_data is not None:
            data.append(ad_data)
    return data


###############################################################################
# Obdelane podatke želimo sedaj shraniti.
###############################################################################


def write_csv(fieldnames, rows, directory, filename):
    """
    Funkcija v csv datoteko podano s parametroma "directory"/"filename" zapiše
    vrednosti v parametru "rows" pripadajoče ključem podanim v "fieldnames"
    """
    #funkcija preveri da obstaja direktorij, sestavi pot do datoteke,
    #z dictwriter iz slovarja pretvori v seznam
    #ničesar ne vrne
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return


# Definirajte funkcijo, ki sprejme neprazen seznam slovarjev, ki predstavljajo
# podatke iz oglasa mačke, in zapiše vse podatke v csv datoteko. Imena za
# stolpce [fieldnames] pridobite iz slovarjev.


def write_cat_ads_to_csv(ads, directory, filename):
    """Funkcija vse podatke iz parametra "ads" zapiše v csv datoteko podano s
    parametroma "directory"/"filename". Funkcija predpostavi, da so ključi vseh
    slovarjev parametra ads enaki in je seznam ads neprazen."""
    # Stavek assert preveri da zahteva velja
    # Če drži se program normalno izvaja, drugače pa sproži napako
    # Prednost je v tem, da ga lahko pod določenimi pogoji izklopimo v
    # produkcijskem okolju
    assert ads and (all(j.keys() == ads[0].keys() for j in ads))
    #preveri da je kar sledi res, če ni, sproži napako
    #preverja da ads ni none ali prazen seznam, in da imajo oglasi iste ključe
    fieldnames = sorted(ads[0].keys())
    #tale sorted ni tok važno baje
    write_csv(fieldnames, ads, directory, filename)


# Celoten program poženemo v glavni funkciji

def main(redownload=True, reparse=True):
    """Funkcija izvede celoten del pridobivanja podatkov:
    1. Oglase prenese iz bolhe
    2. Lokalno html datoteko pretvori v lepšo predstavitev podatkov
    3. Podatke shrani v csv datoteko
    """
    # Najprej v lokalno datoteko shranimo glavno stran
    path_frontpage_file = os.path.join(directory, frontpage_filename)
    #če še ne obstaja jo prenesemo, drgač ni treba
    #s tem se izognemo captcha al pa kej takega
    if not os.path.exists(path_frontpage_file):
        save_frontpage(frontpage_url, directory, frontpage_filename)

    # Iz lokalne (html) datoteke preberemo podatke
    # Podatke preberemo v lepšo obliko (seznam slovarjev)
    data = ads_from_file(directory, frontpage_filename)

    # Podatke shranimo v csv datoteko
    write_cat_ads_to_csv(data, directory, csv_filename)

    # Dodatno: S pomočjo parametrov funkcije main omogoči nadzor, ali se
    # celotna spletna stran ob vsakem zagon prenese (četudi že obstaja)
    # in enako za pretvorbo



if __name__ == '__main__':
    main()
