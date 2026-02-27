#!/usr/bin/env python3
"""
Visualisoi asumisen ja rakentamisen tilastot
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Lue JSON-data
with open('asuminen_rakentaminen.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Muunna data pandas DataFrameksi
merged_data = data['merged_data']
metadata = data['metadata']['series']

# Luo DataFrame
df = pd.DataFrame.from_dict(merged_data, orient='index')

# Muunna indeksi päivämääriksi
def parse_period(period):
    """Muunna 2015M01 tai 2015Q1 muotoiset ajat päivämääriksi"""
    if 'M' in period:
        year, month = period.split('M')
        return datetime(int(year), int(month), 1)
    elif 'Q' in period:
        year, quarter = period.split('Q')
        month = (int(quarter) - 1) * 3 + 1
        return datetime(int(year), month, 1)
    return None

df.index = pd.to_datetime([parse_period(p) for p in df.index])
df = df.sort_index()

# Piirretään kuvaaja
fig, ax = plt.subplots(figsize=(14, 8))

# Määritä värit ja linjat
colors = {
    'rakennuskustannusindeksi': '#1f77b4',
    'vuokraindeksi': '#ff7f0e',
    'osakeasunnot_hinnat': '#2ca02c',
    'kiinteisto_tontit_hinnat': '#d62728',
    'kiinteisto_yllapito': '#9467bd',
    'rakennus_tuotanto': '#8c564b'
}

# Piirretään jokainen sarja
for col in df.columns:
    if col in metadata:
        label = metadata[col].split('(')[0].strip()
        df[col].plot(ax=ax, label=label, linewidth=2, color=colors.get(col, None))

# Asetukset
ax.set_xlabel('Vuosi', fontsize=12)
ax.set_ylabel('Indeksi (2021=100)', fontsize=12)
ax.set_title('Asumisen ja rakentamisen indeksit 2015-2026\nPerusvuosi 2021=100', 
             fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)
ax.axhline(y=100, color='black', linestyle='--', linewidth=0.5, alpha=0.5)

# Näytä kuvaaja
plt.tight_layout()
plt.savefig('asuminen_rakentaminen.png', dpi=300, bbox_inches='tight')
print("Kuva tallennettu: asuminen_rakentaminen.png")
plt.show()
