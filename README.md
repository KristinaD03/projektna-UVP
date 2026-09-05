## projektna-UVP
Za projektno nalogo sem se odločila z interneta pridobiti podatke in statistiko posameznih klubov, ki so igrali v sezonah 24/25 in 25/26 Premier lige. Projektna naloga avtomatsko dobi podatke o izidu tekme, strelcih, rumenih in rdečih kartonih s [spletne strani](https://www.11v11.com/). Pridobleji podatki se shranijo v dve CSV datoteki: tekme.csv in strelci.csv

## Opis delovanja

V datoteki `matches.py` sem sestavila funkcije, ki iz spletne strani 11v11.com izluščijo podatke o tekmah angleške Premier League. Funkcija `from_file` iz strani posamezne sezone prebere podatke o tekmah, kot so datum, domača in gostujoča ekipa ter število doseženih golov. Za vsako tekmo funkciji `kartoni_from_url` in `strelci_tekme_from_url` iz spletne strani posamezne tekme pridobita še podatke o rumenih in rdečih kartonih ter strelcih in minutah doseženih zadetkov. Pri strelcih se s pomočjo dodatnih podatkov s spletne strani pridobi tudi njihova igralna pozicija.

Ker je pridobivanje podatkov za posamezne tekme lahko časovno zahtevno, je pri obdelavi tekem uporabljena knjižnica `concurrent.futures` oziroma `ThreadPoolExecutor`, ki omogoča vzporedno pridobivanje podatkov za več tekem. Tako je zbiranje podatkov hitrejše.

Vse funkcije za pridobivanje in obdelavo podatkov so povezane v glavni datoteki `main.py`. Ta za izbrane sezone pridobi podatke o tekmah in strelcih ter jih s pomočjo funkcij za zapisovanje shrani v ločeni CSV-datoteki `tekme.csv` in `strelci.csv`. Zbrane podatke sem nato uvozila v zvezek `analiza_tekem.ipynb`, kjer sem jih očistila, obdelala, analizirala in predstavila s tabelami ter različnimi grafi.
