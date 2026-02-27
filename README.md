# Asumisen ja rakentamisen tilastot

Yhdistetty aineisto Tilastokeskuksen (StatFin) asumisen ja rakentamisen tilastoista. Kaikki indeksit on normalisoitu yhteiselle perusvuodelle 2015=100 vertailukelpoisuuden parantamiseksi.

## Tilastot

| Tilasto | Kuvaus | Alkuperäinen perusvuosi | Normalisoitu |
|---------|--------|-------------------------|--------------|
| Rakennuskustannusindeksi | Kokonaisindeksi | 2015=100 | 2015=100 |
| Vuokraindeksi | Vapaarahoitteisten vuokra-asuntojen indeksi | 2015=100 | 2015=100 |
| Osakeasuntojen hinnat | Uusien osakeasuntojen hintaindeksi | 2015=100 | 2015=100 |
| Kiinteistöjen hinnat | Omakotitalotonttien hintaindeksi | 2015=100 | 2015=100 |
| Kiinteistön ylläpito | Kiinteistön ylläpidon kustannusindeksi | 2021=100 | 2015=100* |
| Rakennustuotanto | Uudisrakentamisen volyymi-indeksi | 2020=100 | 2015=100* |
| Rakennusluvat | Myönnetyt rakennusluvat, tilavuus m³ (liukuva vuosisumma) | - | 2015=100* |

*Muunnettu yhteiselle perusvuodelle 2015=100

## Menetelmä: Indeksien normalisointi

Kaikki indeksit on muunnettu yhteiselle perusvuodelle **2015=100** vertailukelpoisuuden varmistamiseksi:

### Suoraan perusvuodella 2015=100
- **Rakennuskustannusindeksi**: Haetaan suoraan API:sta perusvuodella 2015=100
- **Vuokraindeksi**: Alkuperäisessä datassa perusvuosi 2015=100
- **Osakeasuntojen hinnat**: Alkuperäisessä datassa perusvuosi 2015=100
- **Kiinteistöjen hinnat**: Alkuperäisessä datassa perusvuosi 2015=100

### Muunnetut indeksit
Seuraavat indeksit on muunnettu laskemalla tavoitevuoden (2015) keskiarvo ja normalisoimalla kaikki arvot suhteessa siihen:

- **Kiinteistön ylläpito** (2021=100 → 2015=100): Data alkaa vasta Q1/2021, muunnettu takautuvasti
- **Rakennustuotanto** (2020=100 → 2015=100): Lasketaan vuoden 2015 keskiarvo ja indeksoidaan `(arvo / 2015_keskiarvo) * 100`
- **Rakennusluvat**: Lasketaan vuoden 2015 keskiarvo tilavuudesta (m³, liukuva vuosisumma) ja indeksoidaan vastaavasti

### Muunnoskaava

```python
def convert_to_index(from_base: int, to_base: int, values: dict) -> dict:
    # Laske tavoitevuoden (to_base) keskiarvo
    to_year_values = [v for k, v in values.items() if k.startswith(str(to_base))]
    to_avg = sum(to_year_values) / len(to_year_values)
    
    # Normalisoi: (arvo / tavoitevuoden_keskiarvo) * 100
    return {k: (v / to_avg) * 100 for k, v in values.items()}
```

## 10 oleellisinta havaintoa aikaväliltä 2015-2026

### 1. � Asuntohinnat ylittivät rakennuskustannukset - spekulaatio voitti fundamentit
Osakeasuntojen hinnat (124.9) ovat nousseet rakennuskustannusten (124.2) ohi. Tämä "leikkaus" kertoo, että asuntojen kysyntä ja sijoitusarvo ovat irrottautuneet tuotantokustannuksista - asunnoilla on arvonousupainetta kasvukeskuksissa riippumatta siitä, mitä rakentaminen maksaa.

### 2. 🏗️ Vuosi 2024: Rakentamisen romahdus - volyymi ja luvat alittivat 100:n
Rakennusluvat (87.8) ja rakentamisen volyymi (79.7) laskivat ensimmäistä kertaa pysyvästi alle vuoden 2015 tason. Syynä **korkeiden korkojen** ja **rakennuskustannusten** yhteisvaikutus: rakentaminen ei ole enää kannattavaa, kun rahoitus on kallista ja materiaalit/työ kallistuneet 24%.

### 3. 📉 Tonttien ja asuntojen hintakehitys erkaantuivat - maan arvo jäi jälkeen
Tonttien hinnat (+7.3%) ovat nousseet alle kolmanneksen asuntojen hinnoista (+25%). Tämä kertoo, että **rakentamisen lisäarvo** on merkittävä: tyhjä tontti ei ole noussut arvossa, mutta sille rakennettu asunto on. Viittaa myös siihen, että rakentamiskustannusten nousu on siirtynyt asuntojen hintoihin.

### 4. ⚡ Energiakriisi 2022-2023 näkyy kiinteistön ylläpidossa (+18% vuodesta 2021)
Kiinteistön ylläpidon kustannukset ovat nousseet 18% vuodesta 2021, vaikka rakennuskustannukset nousivat vain ~10% samalla ajalla. **Ukrainan sodan** aiheuttama energiakriisi nosti lämmitys- ja sähkökustannuksia dramaattisesti, mikä näkyy suoraan ylläpitokuluissa.

### 5. 🔄 Vuokrat jäivät jälkeen rakennuskustannuksista - vuokranantajat kärsivät
Vuokraindeksi (121.7) on 2.5 pistettä rakennuskustannuksia (124.2) alempana. Aiemmin 2015-2020 vuokrat nousivat samaa tahtia. **Syy**: vuokrasääntely, kilpailu ja vuokralaisten maksukyvyn rajallisuus ovat estäneet vuokrien nousun kustannusten mukana. Tämä puristaa vuokrataloyhtiöiden kannattavuutta.

### 6. 📊 Covid-19 rikkoi rakentamisen kasvutrendin 2020-2021
Rakentamisen volyymi-indeksi laski ensimmäisen kerran alle 100:n vuosina 2020-2021 Covid-pandemian aikana. Vaikka se toipui hetkeksi, **rakentaminen ei koskaan palannut pandemiaa edeltävälle tasolle**. Pandemia käynnisti rakenteellisen muutoksen: etätyö vähensi toimistotilakysyntää ja muutti asumisen sijaintitarpeita.

### 7. 🎯 Vuosi 2022: Käännekohta - korot nousivat ja rakentaminen romahti
Vuonna 2022 **EKP aloitti korkojen noston** 0%:sta kohti 4%:a. Tämä oli käännekohta: rakennusluvat alkoivat laskea jyrkästi ja volyymi-indeksi syöksyi. Rakentaminen on erittäin korkoherkää, ja velkarahoitteinen ala reagoi nopeasti rahoituskustannusten nousuun.

### 8. 🏢 Rakennuskustannukset ja asuntohinnat kulkevat käsi kädessä - materiaalit määräävät
Rakennuskustannusten (+24%) ja asuntohintojen (+25%) lähes identtinen nousu kertoo, että **materiaalien ja työn hinnat** siirtyvät suoraan asuntojen hintoihin. Rakentajat eivät voi imeä kustannusnousuja, vaan ne siirtyvät ostajille. Tämä vahvistaa, että asuntotuotanto on kustannusvetoista.

### 9. 📅 2024-2025: "Täydellinen myrsky" - korkeat hinnat + vähän rakentamista
Vuosina 2024-2025 nähdään harvinainen yhdistelmä: asuntojen hinnat korkealla (124.9), mutta rakentaminen matalimmillaan (-20%). Syy: **kysyntä ja tarjonta eivät kohtaa oikeassa hinnassa**. Korkeat rahoituskustannukset estävät sekä ostajia että rakentajia, vaikka asuntopula jatkuu kasvukeskuksissa.

### 10. 🔍 Indeksien hajonta vuonna 2025: 79.7 - 124.9 kertoo rakennekriisistä
Vuonna 2015 kaikki indeksit start 100:sta. Vuonna 2025 alhaisin on 79.7 (rakentamisen volyymi) ja korkein 124.9 (asuntohinnat) - **45 pisteen ero**. Tämä kasvava ero kuvastaa rakennusalan **rakenteellista kriisiä**: hinnat nousevat, mutta tuotanto romahtaa. Markkinat eivät ole tasapainossa, ja kriisin ratkaisu vaatii joko hintojen laskua tai kannustimia rakentamiselle.

---

## Käyttö

```bash
# Hae data Tilastokeskuksesta
python asuminen_rakentaminen.py

# Tulos: asuminen_rakentaminen.json

# Visualisoi data
python visualisoi_data.py

# Tulos: asuminen_rakentaminen.png
```

## Esimerkkikuva

![Asumisen ja rakentamisen indeksit](asuminen_rakentaminen.png)

## API

Skripti käyttää Tilastokeskuksen StatFin API:a:
- https://statfin.stat.fi/PxWeb/api

## Lisenssi

MIT
