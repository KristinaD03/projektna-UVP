# Napotki za analizo podatkov s pandas in matplotlib

Kratek vodič po ukazih, uporabljenih pri analizi podatkov o tekmah Premier League
(`tekme.csv`, `strelci.csv`).

## 1. Skupno število golov po ekipi (doma + gostje)

Gole doma in v gosteh je treba sešteti ločeno, nato pa oba seštevka združiti:

```python
goli_doma = tekme.groupby('domaca_ekipa')['goli_domaca'].sum()
goli_gost = tekme.groupby('gostujoca_ekipa')['goli_gost'].sum()

goli_skupaj = goli_doma.add(goli_gost, fill_value=0)
goli_skupaj = goli_skupaj.sort_values(ascending=False)
```

`.add(..., fill_value=0)` sešteje dve seriji **po imenu ekipe** (indeksu), ne po
vrstnem redu. `fill_value=0` poskrbi, da ekipa, ki bi manjkala v eni od serij,
šteje kot 0, namesto da bi javilo napako.

## 2. Dodajanje stolpca "sezona" iz datuma

Premier League sezona traja avgust–maj, zato mesec datuma pove, kateri sezoni
tekma pripada:

```python
tekme['datum'] = pd.to_datetime(tekme['datum'], format='%d %b %Y')

sezone = []
for datum in tekme['datum']:
    if datum.month >= 8:
        sezona = str(datum.year) + '/' + str(datum.year + 1)
    else:
        sezona = str(datum.year - 1) + '/' + str(datum.year)
    sezone.append(sezona)

tekme['sezona'] = sezone
```

## 3. Goli po ekipi in sezoni skupaj (brez ločevanja doma/gostje)

Namesto ločenega računanja doma/gostje in poznejšega seštevanja je enostavneje
najprej "podvojiti" vsako tekmo v dve vrstici (ekipa + njeni goli), ne glede na to,
ali je igrala doma ali v gosteh:

```python
domace_vrstice = tekme[['domaca_ekipa', 'sezona', 'goli_domaca']].copy()
domace_vrstice.columns = ['ekipa', 'sezona', 'goli']

gostujoce_vrstice = tekme[['gostujoca_ekipa', 'sezona', 'goli_gost']].copy()
gostujoce_vrstice.columns = ['ekipa', 'sezona', 'goli']

vse_vrstice = pd.concat([domace_vrstice, gostujoce_vrstice])

goli_po_ekipi_sezoni = vse_vrstice.groupby(['ekipa', 'sezona'])['goli'].sum()
```

`pd.concat([...])` zlepi obe tabeli eno pod drugo, tako da lahko nato v enem
samem `.groupby()` klicu grupiramo po paru (ekipa, sezona).

## 4. Tabela: ekipe v vrsticah, sezone v stolpcih

```python
tabela_po_sezonah = goli_po_ekipi_sezoni.unstack()
```

`.unstack()` "razpre" drugi nivo indeksa (sezono) v ločene stolpce, tako da
dobimo pregledno tabelo namesto dolge serije z dvojnim indeksom.

## 5. Odstranjevanje decimalk in NaN

Po `unstack()` ima marsikatera ekipa `NaN` v stolpcu sezone, v kateri ni igrala
(npr. ni bila v ligi tisto sezono) — zato pandas cel stolpec pretvori v
decimalni tip (`float`), čeprav so goli cela števila. `NaN` zamenjamo z 0 in
stolpce pretvorimo nazaj v cela števila:

```python
tabela_po_sezonah = tabela_po_sezonah.fillna(0).astype(int)
```

## 6. Skupni seštevek in razvrščanje po padajočem vrstnem redu

Ker ima tabela zdaj več stolpcev (po en na sezono), razvrščanje zahteva izbiro
stolpca, po katerem naj se uredi — ali pa najprej izračunamo skupni seštevek
čez vse sezone:

```python
tabela_po_sezonah['skupaj'] = tabela_po_sezonah.sum(axis=1)
tabela_po_sezonah = tabela_po_sezonah.sort_values('skupaj', ascending=False)
```

`.sum(axis=1)` sešteje **po vrsticah** (vodoravno, čez vse stolpce/sezone za
vsako ekipo), medtem ko `axis=0` (privzeto) sešteva navpično, po stolpcih.




## 7. Estetski nameni
informacije o tem kako deluje np.linspace(0.6, 1, len(skupna_tabela)), kaj predstavljata števili 0,6 in 1...

##  8. Združitev podatkov o golih in kartonih na graf

Na grafu smo združili dva različna podatka o ekipah: **skupno število doseženih golov** in **povprečno število rdečih kartonov na tekmo**.

Ker sta podatka različnih velikostnih redov in imata različni enoti, uporabimo **dve y-osi**. Za to uporabimo ukaz `twinx()`.

```python
ax1 = plt.subplots()
```

Na prvi osi (`ax1`) prikažemo skupno število golov:

```python
ax1.bar(
    x - sirina/2,
    skupna_tabela['goli skupaj'],
    width=sirina,
    color=barve_goli,
    label='Goli'
)
```

Na drugi osi (`ax2`) pa prikažemo povprečno število rdečih kartonov:

```python
ax2 = ax1.twinx()

ax2.bar(
    x + sirina/2,
    skupna_tabela['povprecno rdecih'],
    width=sirina,
    color=barve_kartoni,
    label='Rdeči kartoni'
)
```

`ax1.twinx()` ustvari **drugo y-os**, ki ima enako x-os kot prva, vendar svojo lestvico. Tako lahko na istem grafu primerjamo podatke o golih in kartonih, čeprav imata zelo različne vrednosti.

Položaj stolpcev določimo z:

```python
x - sirina/2
```

za gole in:

```python
x + sirina/2
```

za rdeče kartone. Zato sta stolpca za vsako ekipo postavljena **drug ob drugem**.

Pred izdelavo grafa tabelo uredimo po številu golov:

```python
skupna_tabela = skupna_tabela.sort_values(
    'goli skupaj',
    ascending=True
).reset_index(drop=True)
```

S tem so ekipe na grafu razporejene od najmanjšega do največjega števila doseženih golov.

## 9. Uporaba ThreadPoolExecutor
Tukaj nisem uporabila AI- pomagal mi je kolega, ki se bolj spozna na takšne procese.
