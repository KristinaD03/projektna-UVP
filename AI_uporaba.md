### 1.Kako se uporabi `itertuples()`?

`itertuples()` uporabimo, ko želimo pregledati vrstice `DataFrame-a` eno po eno.

```python
for vrstica in df.itertuples(index=False):
    print(vrstica)
```

Do posameznih podatkov v vrstici dostopamo prek imena stolpca:

```python
for vrstica in df.itertuples(index=False):
    print(vrstica.domaca_ekipa)
    print(vrstica.goli_domaca)
```

Parameter `index=False` pomeni, da indeks `DataFrame-a` ni vključen v vsako vrstico.

**Primer:**

```python
import pandas as pd

df = pd.DataFrame({
    "ekipa": ["Arsenal", "Chelsea"],
    "goli": [3, 1]
})

for vrstica in df.itertuples(index=False):
    print(vrstica.ekipa, vrstica.goli)
```

Izpis:

```text
Arsenal 3
Chelsea 1
```

### 2. Kaj naredi `.isna()`?

`.isna()` preveri, ali so v podatkih **manjkajoče vrednosti** (`NaN`).

Vrne `True`, če je vrednost manjkajoča, in `False`, če ni.

### 3.Kako sestavimo razpredelnico?

```python
podatki = pd.Series(vse_pozicije).value_counts()

rezultati = pd.DataFrame({
    'pozicija': podatki.index,
    'stevilo_golov': podatki.values,
    'delez': podatki.values / podatki.values.sum() * 100
})
```

`pd.Series(vse_pozicije)` pretvori seznam pozicij v pandasov stolpec.

`value_counts()` prešteje, kolikokrat se pojavi vsaka pozicija.

`podatki.index` vsebuje imena pozicij, na primer `Forward`, `Midfielder`, `Defender`.

`podatki.values` vsebuje število pojavitev posamezne pozicije oziroma število golov.

Pri `delez` število golov posamezne pozicije delimo s skupnim številom golov:

```python
podatki.values / podatki.values.sum() * 100
```

Na koncu `pd.DataFrame()` vse te podatke združi v razpredelnico, kjer so stolpci `pozicija`, `stevilo_golov` in `delez`.
### 4.Kako na tortnem diagramu prikažem odstotke?

Pri `plot()` uporabi parameter `autopct`:

```python
pozicije_stevilo.plot(
    kind='pie',
    autopct='%1.1f%%',
    colors=['lightblue', 'lightcoral', 'lightgreen', 'gold']
)
```

`autopct='%1.1f%%'` pomeni, da se na tortnem diagramu prikažejo odstotki z eno decimalno mesto.

### 5. Odstranjevanje decimalk in `NaN`

Po `unstack()` lahko `NaN` zamenjamo z `0` in odstranimo decimalna mesta:

```python
tabela_po_sezonah = goli_po_ekipi_sezoni.unstack()

tabela_po_sezonah = tabela_po_sezonah.fillna(0).astype(int)

tabela_po_sezonah.




### 6. Kako spremenim višino in širino grafa?

Velikost grafa spremenimo z `figsize`:

```python
odstopanje_doma.plot(kind='bar', figsize=(12, 6))


