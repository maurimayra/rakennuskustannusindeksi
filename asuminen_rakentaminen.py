#!/usr/bin/env python3
"""
Asumisen ja rakentamisen tilastot - Yhdistetty aineisto
=========================================================
Yhdistaa Tilastokeskuksen tilastot:
1. Rakennuskustannusindeksi (rki) - kokonaisindeksi
2. Asuntojen vuokrat (asvu) - vuokraindeksi
3. Osakeasuntojen hinnat (ashi) - hintaindeksi
4. Kiinteistojen hinnat (kihi) - hintaindeksi
5. Kiinteiston yllapidon kustannusindeksi (kyki)
6. Rakennus- ja asuntotuotanto (ras) - volyymi-indeksi7. Rakennusluvat (raku) - myönnetyt rakennusluvat tilavuus m3, liukuva vuosisumma
Yhteinen muuttuja: Aika (kuukausi/vuosineljannes)
Indeksointi: Kaikki muunnetaan perusvuoteen 2015=100
"""

import requests
import json
import time
import warnings
warnings.filterwarnings('ignore')

BASE_URL = "https://statfin.stat.fi/PxWeb/api/v1/fi/StatFin"


def fetch_data(table_path: str, query: dict, retries: int = 3) -> dict:
    """Hae dataa Tilastokeskuksen API:sta"""
    url = f"{BASE_URL}/{table_path}"
    
    for attempt in range(retries):
        try:
            response = requests.post(url, json=query, timeout=30)
            if response.status_code == 429:
                # Rate limited - wait and retry
                wait_time = 2 ** attempt
                print(f"    Rate limited, odottaa {wait_time}s...")
                time.sleep(wait_time)
                continue
            if response.status_code != 200:
                print(f"    Virhe {response.status_code}")
                return {"data": []}
            return response.json()
        except Exception as e:
            print(f"    Virhe: {e}")
            time.sleep(1)
    
    return {"data": []}


def get_available_quarters(table_path: str) -> list:
    """Hae saatavilla olevat neljännekset"""
    url = f"{BASE_URL}/{table_path}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for v in data.get('variables', []):
                if 'nelj' in v['code'].lower() or 'vuosi' in v['code'].lower():
                    return v.get('values', [])
    except:
        pass
    return []


def parse_data(data: dict) -> dict:
    """Yleinen parseri"""
    result = {}
    for item in data.get('data', []):
        time_str = item['key'][0]
        val = item['values'][0]
        if val not in ['.', '..', '']:
            try:
                result[time_str] = float(val)
            except:
                pass
    return result


def index_quarter_to_month(quarterly_data: dict) -> dict:
    """Muunna neljannesvuosi kuukausiksi"""
    monthly = {}
    for quarter, value in quarterly_data.items():
        year, q = quarter[:4], int(quarter[5])
        start_month = (q - 1) * 3 + 1
        for m in range(start_month, start_month + 3):
            monthly[f"{year}M{m:02d}"] = value
    return monthly


def convert_to_index(from_base: int, to_base: int, values: dict) -> dict:
    """Muunna indeksisarja perusvuodesta toiseen"""
    if from_base == to_base:
        return values
    
    # Laske from_base vuoden keskiarvo
    from_year_values = [v for k, v in values.items() if k.startswith(str(from_base))]
    if not from_year_values:
        return values
    from_avg = sum(from_year_values) / len(from_year_values)
    
    # Laske to_base vuoden keskiarvo
    to_year_values = [v for k, v in values.items() if k.startswith(str(to_base))]
    if not to_year_values:
        return values
    to_avg = sum(to_year_values) / len(to_year_values)
    
    # Muunna: (arvo / from_avg) * to_base_arvo, missä to_base_arvo = 100
    # Eli: (arvo / from_avg) * (to_avg / to_avg) * 100
    # = (arvo / from_avg) * 100 * (to_avg / to_avg)
    # Mutta koska haluamme to_base = 100, teemme: (arvo / to_avg) * 100
    return {k: (v / to_avg) * 100 for k, v in values.items()}


def month_to_quarter(month_key: str) -> str:
    year, month = int(month_key[:4]), int(month_key[5:7])
    return f"{year}Q{(month-1)//3 + 1}"


# =============================================================================
# 1. RAKENNUSKUSTANNUSINDEKSI
# =============================================================================
def fetch_rakennuskustannusindeksi() -> dict:
    print("  [1/7] Rakennuskustannusindeksi...")
    
    query = {
        "query": [
            {"code": "Kuukausi", "selection": {"filter": "item", 
                "values": [f"{y}M{m:02d}" for y in range(2015, 2027) for m in range(1, 13) 
                if not (y == 2026 and m > 1)]}},
            {"code": "Perusvuosi", "selection": {"filter": "item", "values": ["2015_100"]}},
            {"code": "Tiedot", "selection": {"filter": "item", "values": ["pisteluku"]}}
        ],
        "response": {"format": "json"}
    }
    
    data = fetch_data("rki/statfin_rki_pxt_13g8.px", query)
    return parse_data(data)  # Already base 2015


# =============================================================================
# 2. VUOKRAINDEKSI
# =============================================================================
def fetch_vuokraindeksi() -> dict:
    print("  [2/7] Vuokraindeksi...")
    
    query = {
        "query": [
            {"code": "Vuosineljännes", "selection": {"filter": "item",
                "values": [f"{y}Q{q}" for y in range(2015, 2026) for q in range(1, 5)]}},
            {"code": "Alue", "selection": {"filter": "item", "values": ["ksu"]}},
            {"code": "Huoneluku", "selection": {"filter": "item", "values": ["00"]}},
            {"code": "Rahoitusmuoto", "selection": {"filter": "item", "values": ["0"]}},
            {"code": "Tiedot", "selection": {"filter": "item", "values": ["ketj_Tor"]}}
        ],
        "response": {"format": "json"}
    }
    
    data = fetch_data("asvu/statfin_asvu_pxt_11x4.px", query)
    raw = parse_data(data)
    monthly = index_quarter_to_month(raw)
    return monthly  # Already base 2015


# =============================================================================
# 3. OSAKEASUNTOJEN HINTAINDEKSI
# =============================================================================
def fetch_osakeasuntojen_hinnat() -> dict:
    print("  [3/7] Osakeasuntojen hinnat...")
    
    query = {
        "query": [
            {"code": "Vuosineljännes", "selection": {"filter": "item",
                "values": [f"{y}Q{q}" for y in range(2015, 2026) for q in range(1, 5)]}},
            {"code": "Alue", "selection": {"filter": "item", "values": ["ksu"]}},
            {"code": "Talotyyppi", "selection": {"filter": "item", "values": ["0"]}},
            {"code": "Huoneluku", "selection": {"filter": "item", "values": ["00"]}},
            {"code": "Tiedot", "selection": {"filter": "item", "values": ["ketjutettu_lv"]}}
        ],
        "response": {"format": "json"}
    }
    
    data = fetch_data("ashi/statfin_ashi_pxt_12fv.px", query)
    raw = parse_data(data)
    if not raw:
        return {}
    monthly = index_quarter_to_month(raw)
    return monthly  # Already base 2015


# =============================================================================
# 4. KIINTEISTOJEN HINNAT
# =============================================================================
def fetch_kiinteistojen_hinnat() -> dict:
    print("  [4/7] Omakotitalotonttien hinnat...")
    
    query = {
        "query": [
            {"code": "Vuosi", "selection": {"filter": "item",
                "values": [str(y) for y in range(2015, 2026)]}},
            {"code": "Aluejako", "selection": {"filter": "item", "values": ["01"]}},
            {"code": "Tiedot", "selection": {"filter": "item", "values": ["ketjutettu_lv"]}}
        ],
        "response": {"format": "json"}
    }
    
    data = fetch_data("kihi/statfin_kihi_pxt_11jc.px", query)
    raw = {}
    for item in data.get('data', []):
        year = item['key'][1]
        val = item['values'][0]
        if val not in ['.', '..', '']:
            try:
                raw[year] = float(val)
            except:
                pass
    
    quarterly = {}
    for year, value in raw.items():
        for q in range(1, 5):
            quarterly[f"{year}Q{q}"] = value
    
    monthly = index_quarter_to_month(quarterly)
    return monthly  # Already base 2015


# =============================================================================
# 5. KIINTEISTON YLLAPIDON KUSTANNUSINDEKSI
# =============================================================================
def fetch_kiinteisto_yllapito() -> dict:
    print("  [5/7] Kiinteiston yllapito...")
    
    # Hae saatavilla olevat neljännekset
    available = get_available_quarters("kyki/statfin_kyki_pxt_14ry.px")
    if not available:
        available = [f"{y}Q{q}" for y in range(2021, 2026) for q in range(1, 5)]
    
    result = {}
    for year in range(2021, 2026):
        # Suodata vain saatavilla olevat
        year_quarters = [q for q in available if q.startswith(str(year))]
        if not year_quarters:
            continue
            
        query = {
            "query": [
                {"code": "Vuosineljännes", "selection": {"filter": "item",
                    "values": year_quarters}},
                {"code": "Rakennustyyppi", "selection": {"filter": "item", "values": ["0."]}},
                {"code": "Tiedot", "selection": {"filter": "item", "values": ["indeksipisteluku_kaksikatk"]}}
            ],
            "response": {"format": "json"}
        }
        
        data = fetch_data("kyki/statfin_kyki_pxt_14ry.px", query)
        for item in data.get('data', []):
            time_str = item['key'][0]
            val = item['values'][0]
            if val not in ['.', '..', '']:
                try:
                    result[time_str] = float(val)
                except:
                    pass
        
        time.sleep(0.5)  # Rate limit protection
    
    monthly = index_quarter_to_month(result)
    return convert_to_index(2021, 2015, monthly)


# =============================================================================
# 6. RAKENNUSTUOTANTO
# =============================================================================
def fetch_rakennus_tuotanto() -> dict:
    print("  [6/7] Uudisrakentamisen volyymi...")
    
    result = {}
    for year in range(2015, 2026):
        query = {
            "query": [
                {"code": "rakennusluokitus2018", "selection": {"filter": "item", "values": ["SSS"]}},
                {"code": "timeperiod", "selection": {"filter": "item",
                    "values": [f"{year}M{m:02d}" for m in range(1, 13)]}},
                {"code": "ContentCode", "selection": {"filter": "item", "values": ["urvi2020"]}}
            ],
            "response": {"format": "json"}
        }
        
        data = fetch_data("raku/statfin_raku_pxt_156g.px", query)
        for item in data.get('data', []):
            time_str = item['key'][1]  # Aika on toinen avain
            val = item['values'][0]
            if val not in ['.', '..', '']:
                try:
                    result[time_str] = float(val)
                except:
                    pass
        
        time.sleep(1)  # Rate limit protection
    
    return convert_to_index(2020, 2015, result)


# =============================================================================
# 7. RAKENNUSLUVAT
# =============================================================================
def fetch_rakennusluvat() -> dict:
    print("  [7/7] Myönnetyt rakennusluvat...")
    
    result = {}
    for year in range(2015, 2026):
        query = {
            "query": [
                {"code": "rakennusvaihe", "selection": {"filter": "item", "values": ["1"]}},
                {"code": "alue", "selection": {"filter": "item", "values": ["SSS"]}},
                {"code": "timeperiod", "selection": {"filter": "item",
                    "values": [f"{year}M{m:02d}" for m in range(1, 13)]}},
                {"code": "rakennusluokitus2018", "selection": {"filter": "item", "values": ["SSS"]}},
                {"code": "ContentCode", "selection": {"filter": "item", "values": ["tilavuusToimenpide_lvs"]}}
            ],
            "response": {"format": "json"}
        }
        
        data = fetch_data("raku/statfin_raku_pxt_156f.px", query)
        for item in data.get('data', []):
            time_str = item['key'][2]  # Aika on kolmas avain
            val = item['values'][0]
            if val not in ['.', '..', '']:
                try:
                    result[time_str] = float(val)
                except:
                    pass
        
        time.sleep(1)  # Rate limit protection
    
    # Muunna indeksiksi (2015=100)
    year_2015_avg = sum([v for k, v in result.items() if k.startswith("2015")]) / 12
    if year_2015_avg > 0:
        return {k: (v / year_2015_avg) * 100 for k, v in result.items()}
    return result


# =============================================================================
# YHDISTAMINEN
# =============================================================================
def merge_all_statistics():
    print("\n" + "="*60)
    print("HAETAAN TILASTOJA TILASTOKESKUKSESTA")
    print("="*60)
    
    data = {
        "rakennuskustannusindeksi": fetch_rakennuskustannusindeksi(),
        "vuokraindeksi": fetch_vuokraindeksi(),
        "osakeasunnot_hinnat": fetch_osakeasuntojen_hinnat(),
        "kiinteisto_tontit_hinnat": fetch_kiinteistojen_hinnat(),
        "kiinteisto_yllapito": fetch_kiinteisto_yllapito(),
        "rakennus_tuotanto": fetch_rakennus_tuotanto(),
        "rakennusluvat": fetch_rakennusluvat(),
    }
    
    all_periods = set()
    for series in data.values():
        all_periods.update(series.keys())
    
    def sort_key(x):
        if 'M' in x:
            return (int(x[:4]), int(x[5:7]), 0)
        else:
            return (int(x[:4]), int(x[5])*3, 1)
    
    merged = {}
    for period in sorted(all_periods, key=sort_key):
        merged[period] = {name: series.get(period) for name, series in data.items()}
    
    return merged, data


def export_to_json(merged, raw_data, filename="asuminen_rakentaminen.json"):
    output = {
        "metadata": {
            "source": "Tilastokeskus (StatFin)",
            "base_year": "2015=100",
            "description": "Asumisen ja rakentamisen yhdistetty indeksiaineisto",
            "series": {
                "rakennuskustannusindeksi": "Rakennuskustannusindeksin kokonaisindeksi (2015=100)",
                "vuokraindeksi": "Vuokraindeksi (2015=100)",
                "osakeasunnot_hinnat": "Osakeasuntojen hintaindeksi (2015=100)",
                "kiinteisto_tontit_hinnat": "Omakotitalotonttien hintaindeksi (2015=100)",
                "kiinteisto_yllapito": "Kiinteiston yllapidon kustannusindeksi (muunnettu 2015=100, data 2021-)",
                "rakennus_tuotanto": "Uudisrakentamisen volyymi-indeksi (muunnettu 2015=100)",
                "rakennusluvat": "Myönnetyt rakennusluvat, tilavuus m3 liukuva vuosisumma (indeksi 2015=100)"
            },
            "note": "Indeksit muunnettu perusvuodesta 2020/2021 perusvuoteen 2015. Kiinteistön ylläpidon data alkaa Q1/2021."
        },
        "merged_data": merged
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nData viety: {filename}")
    return output


def print_summary(merged):
    print("\n" + "="*60)
    print("Y H T E E N V E T O")
    print("="*60)
    
    quarters = {}
    for period in sorted(merged.keys(), reverse=True):
        q = month_to_quarter(period) if 'M' in period else period
        if q not in quarters:
            quarters[q] = merged[period]
    
    print("\nViimeisimmat arvot:")
    for period in sorted(quarters.keys(), reverse=True)[:4]:
        print(f"\n{period}:")
        for key, value in quarters[period].items():
            if value:
                print(f"  {key}: {value:.1f}")


def main():
    print("="*60)
    print("ASUMISEN JA RAKENTAMISEN TILASTOT")
    print("Tilastokeskus - Yhdistetty aineisto")
    print("Perusvuosi: 2015 = 100")
    print("="*60)
    
    merged, raw_data = merge_all_statistics()
    output = export_to_json(merged, raw_data)
    print_summary(merged)
    
    print("\n" + "="*60)
    print("Valmis!")
    print("="*60)
    
    return merged, raw_data


if __name__ == "__main__":
    main()
