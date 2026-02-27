#!/usr/bin/env python3
"""
Ennustemoduuli - Extrapoloi tulevat kuukaudet
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


def load_data(filename: str = "asuminen_rakentaminen.json") -> dict:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return {}


def get_latest_values(data: dict, n_months: int = 12) -> Dict[str, List]:
    merged = data.get('merged_data', {})
    
    sorted_periods = sorted(merged.keys(), key=lambda x: (
        int(x[:4]), int(x[5:7]) if 'M' in x else int(x[5])*3
    ))
    
    result = {}
    for series_key in merged[sorted_periods[0]].keys():
        values = []
        for period in sorted_periods:
            val = merged[period].get(series_key)
            if val is not None:
                values.append((period, val))
        result[series_key] = values[-n_months:]
    
    return result


def linear_forecast(values: List, steps: int = 6) -> List:
    if len(values) < 3:
        return [v for _, v in values]
    
    y = np.array([v for _, v in values[-12:]])
    x = np.arange(len(y))
    coeffs = np.polyfit(x, y, 1)
    
    future_x = np.arange(len(y), len(y) + steps)
    return np.polyval(coeffs, future_x).tolist()


def moving_average_forecast(values: List, steps: int = 6, window: int = 3) -> List:
    if len(values) < window:
        return [v for _, v in values]
    
    recent = [v for _, v in values[-window:]]
    avg = sum(recent) / window
    
    if len(values) >= window * 2:
        prev_avg = sum([v for _, v in values[-window*2:-window]]) / window
        trend = (avg - prev_avg) / window
    else:
        trend = 0
    
    return [avg + trend * i for i in range(1, steps + 1)]


def generate_forecast_periods(last_period: str, steps: int = 6) -> List:
    year = int(last_period[:4])
    
    if 'M' in last_period:
        month = int(last_period[5:7])
        return [f"{year + (month + i - 1) // 12}M{((month + i - 1) % 12) + 1:02d}" 
                for i in range(1, steps + 1)]
    elif 'Q' in last_period:
        quarter = int(last_period[5])
        return [f"{year + (quarter + i - 1) // 4}Q{((quarter + i - 1) % 4) + 1}"
                for i in range(1, steps + 1)]
    return []


def create_forecast(data: dict, months: int = 6) -> dict:
    latest_values = get_latest_values(data, n_months=12)
    
    if not latest_values:
        return {}
    
    first_series = list(latest_values.values())[0]
    last_period = first_series[-1][0]
    forecast_periods = generate_forecast_periods(last_period, months)
    
    forecasts = {}
    for period_idx, period in enumerate(forecast_periods):
        forecasts[period] = {}
        
        for series_name, values in latest_values.items():
            linear = linear_forecast(values, months)
            ma = moving_average_forecast(values, months)
            
            if period_idx < len(linear) and period_idx < len(ma):
                forecast_value = linear[period_idx] * 0.6 + ma[period_idx] * 0.4
                forecasts[period][series_name] = round(forecast_value, 2)
    
    return forecasts


def print_forecast_summary(forecasts: dict):
    print("\n" + "="*50)
    print("F O R E C A S T S")
    print("="*50)
    
    if not forecasts:
        print("No forecasts")
        return
    
    for period in sorted(forecasts.keys()):
        print(f"\n{period}:")
        for series, value in forecasts[period].items():
            print(f"  {series}: {value:.1f}")


def export_forecast_json(forecasts: dict, original_data: dict, 
                          filename: str = "ennusteet.json"):
    output = {
        "metadata": {
            "source": "Statistics Finland + forecast model",
            "forecast_method": "Linear regression + moving average (60/40)",
            "forecast_months": len(forecasts),
            "generated_at": datetime.now().isoformat()
        },
        "forecasts": forecasts
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Forecasts exported: {filename}")


def main():
    print("="*50)
    print("FORECASTS")
    print("="*50)
    
    data = load_data()
    if not data:
        return
    
    forecasts = create_forecast(data, months=6)
    print_forecast_summary(forecasts)
    export_forecast_json(forecasts, data)


if __name__ == "__main__":
    main()
