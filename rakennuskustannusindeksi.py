#!/usr/bin/env python3
"""
Rakennuskustannusindeksin (kokonaisindeksi) visualisointi ja ennustaminen
Data: Tilastokeskus (StatFin API)
Perusvuosi: 2021=100
"""

import requests
import json
from datetime import datetime

# --- API-data ---
def fetch_building_cost_index():
    """Hae rakennuskustannusindeksin kokonaisindeksi Tilastokeskuksesta"""
    url = "https://statfin.stat.fi/PxWeb/api/v1/fi/StatFin/rki/statfin_rki_pxt_13g8.px"
    
    # Haetaan data 2021-01 alkaen (perusvuosi 2021=100)
    months = []
    for year in [2021, 2022, 2023, 2024, 2025, 2026]:
        for month in range(1, 13):
            if year == 2026 and month > 1:
                break  # Vain tammikuu 2026
            months.append(f"{year}M{month:02d}")
    
    payload = {
        "query": [
            {
                "code": "Kuukausi",
                "selection": {
                    "filter": "item",
                    "values": months
                }
            },
            {
                "code": "Perusvuosi",
                "selection": {
                    "filter": "item",
                    "values": ["2021_100"]
                }
            },
            {
                "code": "Tiedot",
                "selection": {
                    "filter": "item",
                    "values": ["pisteluku"]
                }
            }
        ],
        "response": {
            "format": "json"
        }
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    # Parsitaan data - ohitetaan puuttuvat arvot
    dates = []
    values = []
    for item in data['data']:
        month_str = item['key'][0]
        val_str = item['values'][0]
        
        # Ohita puuttuvat arvot
        if val_str == '.' or val_str == '':
            continue
        
        value = float(val_str)
        
        # Muunna kuukausi stringiksi datetime-objektiksi
        year = int(month_str[:4])
        month = int(month_str[5:7])
        dates.append(datetime(year, month, 1))
        values.append(value)
    
    return dates, values


def linear_regression(x, y):
    """Yksinkertainen lineaarinen regressio"""
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi * xi for xi in x)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n
    
    return slope, intercept


def predict_next_months(values, n_months=6):
    """
    Yksinkertainen lineaarinen regressioennustus seuraaville kuukausille
    Käyttää viimeisen 12 kuukauden dataa trendin laskemiseen
    """
    # Käytä viimeistä 12 kuukautta trendin arviointiin
    recent = values[-12:]
    x = list(range(len(recent)))
    
    # Lineaarinen regressio
    slope, intercept = linear_regression(x, recent)
    
    # Ennusta seuraavat n kuukautta
    predictions = []
    last_value = values[-1]
    
    for i in range(1, n_months + 1):
        pred = last_value + slope * i
        predictions.append(pred)
    
    return predictions, slope


def main():
    print("=" * 60)
    print("RAKENNUSKUSTANNUSINDEKSI - KOKONAISINDEKSI")
    print("Perusvuosi: 2021 = 100")
    print("Lähde: Tilastokeskus (StatFin)")
    print("=" * 60)
    
    # Hae data
    print("\nHaetaan dataa Tilastokeskuksesta...")
    dates, values = fetch_building_cost_index()
    
    # Näytä tuoreimmat arvot
    print(f"\nDatapisteitä: {len(values)}")
    print(f"Aikaväli: {dates[0].strftime('%Y-%m')} - {dates[-1].strftime('%Y-%m')}")
    print(f"\nViimeisimmät arvot:")
    for i in range(-6, 0):
        print(f"  {dates[i].strftime('%Y-%m')}: {values[i]:.1f}")
    
    # Ennustus
    print("\n" + "=" * 60)
    print("ENNUSTUS: Seuraavat 6 kuukautta")
    print("=" * 60)
    
    predictions, slope = predict_next_months(values, 6)
    
    # Luodaan ennustetut päivämäärät
    last_date = dates[-1]
    pred_dates = []
    for i in range(1, 7):
        # Lisää kuukausi
        if last_date.month + i > 12:
            new_month = (last_date.month + i) - 12
            new_year = last_date.year + 1
        else:
            new_month = last_date.month + i
            new_year = last_date.year
        pred_dates.append(datetime(new_year, new_month, 1))
    
    print(f"Kuukausittainen keskimääräinen muutos: {slope:+.3f} pistettä/kk")
    print(f"\nEnnustetut arvot:")
    for i, (d, p) in enumerate(zip(pred_dates, predictions)):
        print(f"  {d.strftime('%Y-%m')}: {p:.1f} (ennuste)")
    
    # Laske kokonaismuutos
    total_change = predictions[-1] - values[-1]
    pct_change = (total_change / values[-1]) * 100
    print(f"\nMuutos 6 kk:ssa: {total_change:+.1f} pistettä ({pct_change:+.2f}%)")
    
    # Tulosta JSON
    print("\n" + "=" * 60)
    print("JSON output:")
    print("=" * 60)
    
    result = {
        "source": "Tilastokeskus - Rakennuskustannusindeksi",
        "index_base": "2021=100",
        "data": {d.strftime('%Y-%m'): v for d, v in zip(dates, values)},
        "forecast": {
            d.strftime('%Y-%m'): round(p, 1) for d, p in zip(pred_dates, predictions)
        },
        "monthly_change": round(slope, 3),
        "total_change_6m": round(total_change, 1),
        "percent_change_6m": round(pct_change, 2)
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return dates, values, pred_dates, predictions


if __name__ == "__main__":
    main()
