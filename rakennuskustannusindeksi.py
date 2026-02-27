#!/usr/bin/env python3
"""
Rakennuskustannusindeksin (kokonaisindeksi) visualisointi ja ennustaminen
Data: Tilastokeskus (StatFin API)
Perusvuosi: 2015=100
Ennustemenetelmä: Holtin eksponentiaalinen tasoitus (trendi + taso)
"""

import requests
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# --- API-data ---
def fetch_building_cost_index():
    """Hae rakennuskustannusindeksin kokonaisindeksi Tilastokeskuksesta"""
    url = "https://statfin.stat.fi/PxWeb/api/v1/fi/StatFin/rki/statfin_rki_pxt_13g8.px"
    
    # Haetaan data 2015-01 alkaen (perusvuosi 2015=100)
    months = []
    for year in range(2015, 2027):
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
                    "values": ["2015_100"]
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


def holt_exponential_smoothing(values, alpha=0.3, beta=0.1):
    """
    Holtin eksponentiaalinen tasoitus - huomioi sekä tason että trendin
    
    Args:
        values: Aikasarja
        alpha: Tasoituskerroin tasolle (0-1), oletuksena 0.3
        beta: Tasoituskerroin trendille (0-1), oletuksena 0.1
    
    Returns:
        level: Tasoitettu taso viimeiselle ajanhetkelle
        trend: Trendi viimeiselle ajanhetkelle
    """
    # Alusta taso ja trendi
    level = values[0]
    trend = values[1] - values[0]  # Alkutrendi ensimmäisestä muutoksesta
    
    # Käy läpi kaikki arvot ja päivitä taso ja trendi
    for value in values:
        last_level = level
        level = alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
    
    return level, trend


def predict_next_months(values, n_months=12):
    """
    Ennustus Holtin eksponentiaalisella tasoituksella
    Käyttää koko aikasarjaa, mutta antaa enemmän painoa viimeisille 24 kuukaudelle
    
    Args:
        values: Historiallinen aikasarja
        n_months: Kuinka monta kuukautta ennustetaan
    
    Returns:
        predictions: Ennustetut arvot
        trend: Kuukausittainen trendi
        level: Nykyinen taso
    """
    # Käytä viimeisiä 36 kuukautta (3 vuotta) ennusteen laskemiseen
    recent_window = min(36, len(values))
    recent = values[-recent_window:]
    
    # Holtin menetelmä
    level, trend = holt_exponential_smoothing(recent, alpha=0.3, beta=0.1)
    
    # Ennusta seuraavat n kuukautta
    predictions = []
    for i in range(1, n_months + 1):
        pred = level + trend * i
        predictions.append(pred)
    
    return predictions, trend, level



def create_visualization(dates, values, pred_dates, predictions, trend):
    """Luo visualisointi historiallisesta datasta ja ennusteesta"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Historiallinen data
    ax.plot(dates, values, 'b-', linewidth=2, label='Toteutunut', marker='o', markersize=3)
    
    # Ennuste
    # Yhdistä viimeinen toteutunut piste ennusteeseen
    forecast_dates = [dates[-1]] + pred_dates
    forecast_values = [values[-1]] + predictions
    ax.plot(forecast_dates, forecast_values, 'r--', linewidth=2, label='Ennuste (Holt)', marker='s', markersize=4)
    
    # Luottamusväli (±2 * keskihajonta viimeiseltä 24kk:lta)
    recent_std = np.std(np.diff(values[-24:]))  # Muutosten keskihajonta
    lower_bound = [p - 2*recent_std*np.sqrt(i+1) for i, p in enumerate(predictions)]
    upper_bound = [p + 2*recent_std*np.sqrt(i+1) for i, p in enumerate(predictions)]
    ax.fill_between(pred_dates, lower_bound, upper_bound, alpha=0.2, color='red', label='95% luottamusväli')
    
    # Muotoilu
    ax.set_xlabel('Aika', fontsize=12)
    ax.set_ylabel('Indeksi (2015=100)', fontsize=12)
    ax.set_title(f'Rakennuskustannusindeksi: Historia ja ennuste\nTrendi: {trend:+.3f} pistettä/kk', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Lisää 100-viiva
    ax.axhline(y=100, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    
    # Pystyviiva erottamaan historian ja ennusteen
    ax.axvline(x=dates[-1], color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('rakennuskustannusindeksi_ennuste.png', dpi=300, bbox_inches='tight')
    print("\nKuva tallennettu: rakennuskustannusindeksi_ennuste.png")
    
    return fig


def main():
    print("=" * 60)
    print("RAKENNUSKUSTANNUSINDEKSI - KOKONAISINDEKSI")
    print("Perusvuosi: 2015 = 100")
    print("Lähde: Tilastokeskus (StatFin)")
    print("Ennustemenetelmä: Holtin eksponentiaalinen tasoitus")
    print("=" * 60)
    
    # Hae data
    print("\nHaetaan dataa Tilastokeskuksesta...")
    dates, values = fetch_building_cost_index()
    
    # Näytä tuoreimmat arvot
    print(f"\nDatapisteitä: {len(values)}")
    print(f"Aikaväli: {dates[0].strftime('%Y-%m')} - {dates[-1].strftime('%Y-%m')}")
    print(f"\nViimeisimmät 12 kuukautta:")
    for i in range(-12, 0):
        print(f"  {dates[i].strftime('%Y-%m')}: {values[i]:.1f}")
    
    # Ennustus
    print("\n" + "=" * 60)
    print("ENNUSTUS: Seuraavat 12 kuukautta")
    print("=" * 60)
    
    predictions, trend, level = predict_next_months(values, 12)
    
    # Luodaan ennustetut päivämäärät
    pred_dates = []
    current_date = dates[-1]
    for i in range(1, 13):
        # Lisää kuukausi
        next_date = current_date + timedelta(days=32)
        next_date = next_date.replace(day=1)
        pred_dates.append(next_date)
        current_date = next_date
    
    print(f"Nykyinen taso: {level:.1f}")
    print(f"Kuukausittainen trendi: {trend:+.3f} pistettä/kk")
    print(f"Vuositrendi: {trend*12:+.1f} pistettä/vuosi ({trend*12/level*100:+.2f}%/vuosi)")
    print(f"\nEnnustetut arvot:")
    for i, (d, p) in enumerate(zip(pred_dates, predictions), 1):
        change_from_now = p - values[-1]
        print(f"  {d.strftime('%Y-%m')}: {p:.1f} ({change_from_now:+.1f} pistettä)")
    
    # Laske kokonaismuutos
    total_change = predictions[-1] - values[-1]
    pct_change = (total_change / values[-1]) * 100
    print(f"\nMuutos 12 kk:ssa: {total_change:+.1f} pistettä ({pct_change:+.2f}%)")
    
    # Visualisointi
    print("\n" + "=" * 60)
    print("Luodaan visualisointi...")
    print("=" * 60)
    create_visualization(dates, values, pred_dates, predictions, trend)
    
    # Tulosta JSON
    print("\n" + "=" * 60)
    print("JSON output:")
    print("=" * 60)
    
    result = {
        "source": "Tilastokeskus - Rakennuskustannusindeksi",
        "index_base": "2015=100",
        "method": "Holt Exponential Smoothing (alpha=0.3, beta=0.1)",
        "current_level": round(level, 1),
        "monthly_trend": round(trend, 3),
        "annual_trend": round(trend * 12, 1),
        "annual_trend_pct": round(trend * 12 / level * 100, 2),
        "latest_value": {
            "date": dates[-1].strftime('%Y-%m'),
            "value": round(values[-1], 1)
        },
        "forecast_12m": {
            d.strftime('%Y-%m'): round(p, 1) for d, p in zip(pred_dates, predictions)
        },
        "total_change_12m": round(total_change, 1),
        "percent_change_12m": round(pct_change, 2)
    }
    
    # Tallenna JSON
    with open('rakennuskustannusindeksi_ennuste.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\nJSON tallennettu: rakennuskustannusindeksi_ennuste.json")
    
    return dates, values, pred_dates, predictions


if __name__ == "__main__":
    main()
