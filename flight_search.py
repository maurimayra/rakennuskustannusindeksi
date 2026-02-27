#!/usr/bin/env python3
"""
Lentohakusovellus - Skyscanner/Googlelle
========================================
Tämä sovellus hakee lentoja käyttäen:
1. Skyscanner (selain, vaatii käyttäjän)
2. Amadeus API (vaatii tokenin)
3. Mallidata (ilmainen, demonstrointiin)

Käyttö:
    python flight_search.py              # Hae malleista
    python flight_search.py --demo       # Näytä esimerkkejä
    python flight_search.py --from HEL --to LON --date 2026-03-15
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Kohteet
DESTINATIONS = {
    "LON": "Lontoo",
    "PAR": "Pariisi",
    "AMS": "Amsterdam",
    "BER": "Berliini",
    "BCN": "Barcelona",
    "ROM": "Rooma",
    "MIL": "Milano",
    "CPH": "Kööpenhamina",
    "OSL": "Oslo",
    "STO": "Tukholma",
    "WAW": "Varsova",
    "PRG": "Praha",
    "VIE": "Wien",
    "BUD": "Budapest",
    "TAK": "Teneriffa",
    "FUE": "Fuerteventura",
    "NAP": "Naples",
    "ALC": "Alicante"
}

AIRLINES = {
    "AY": "Finnair",
    "BA": "British Airways",
    "LH": "Lufthansa",
    "SK": "SAS",
    "FR": "Ryanair",
    "W6": "Wizz Air",
    "D8": "Norwegian",
    "KL": "KLM",
    "AF": "Air France"
}


def get_demo_flights(
    origin: str = "HEL",
    destination: str = None,
    date: str = None,
    max_price: float = None,
    direct_only: bool = False
) -> List[Dict]:
    """
    Palauta mallidata lentoja demonstrointitarkoituksiin.
    Oikea toteutus käyttäisi Amadeus/Kiwi API:a.
    """
    
    # Esimerkkidata oikeista hinnoista ja reiteistä
    demo_flights = [
        # Lontoo
        {"from": "HEL", "to": "LON", "price": 89, "airline": "AY", "dep": "08:15", "arr": "09:35", "duration": "2h 20m", "stops": 0},
        {"from": "HEL", "to": "LON", "price": 129, "airline": "BA", "dep": "14:30", "arr": "15:50", "duration": "2h 20m", "stops": 0},
        {"from": "HEL", "to": "LON", "price": 159, "airline": "FR", "dep": "18:45", "arr": "20:05", "duration": "2h 20m", "stops": 0},
        
        # Pariisi
        {"from": "HEL", "to": "PAR", "price": 99, "airline": "AY", "dep": "07:00", "arr": "09:25", "duration": "2h 25m", "stops": 0},
        {"from": "HEL", "to": "PAR", "price": 149, "airline": "AF", "dep": "13:15", "arr": "15:40", "duration": "2h 25m", "stops": 0},
        {"from": "HEL", "to": "PAR", "price": 79, "airline": "SK", "dep": "21:00", "arr": "23:30", "duration": "2h 30m", "stops": 1},
        
        # Barcelona
        {"from": "HEL", "to": "BCN", "price": 119, "airline": "AY", "dep": "10:30", "arr": "13:45", "duration": "3h 15m", "stops": 0},
        {"from": "HEL", "to": "BCN", "price": 89, "airline": "FR", "dep": "16:20", "arr": "19:40", "duration": "3h 20m", "stops": 0},
        {"from": "HEL", "to": "BCN", "price": 199, "airline": "LH", "dep": "06:15", "arr": "11:50", "duration": "5h 35m", "stops": 1},
        
        # Rooma
        {"from": "HEL", "to": "ROM", "price": 109, "airline": "AY", "dep": "09:45", "arr": "12:40", "duration": "2h 55m", "stops": 0},
        {"from": "HEL", "to": "ROM", "price": 139, "airline": "FR", "dep": "17:30", "arr": "20:30", "duration": "3h 00m", "stops": 0},
        
        # Amsterdam
        {"from": "HEL", "to": "AMS", "price": 85, "airline": "AY", "dep": "08:00", "arr": "09:35", "duration": "1h 35m", "stops": 0},
        {"from": "HEL", "to": "AMS", "price": 119, "airline": "KL", "dep": "15:20", "arr": "16:55", "duration": "1h 35m", "stops": 0},
        
        # Berliini
        {"from": "HEL", "to": "BER", "price": 59, "airline": "AY", "dep": "09:00", "arr": "10:15", "duration": "1h 15m", "stops": 0},
        {"from": "HEL", "to": "BER", "price": 79, "airline": "FR", "dep": "19:30", "arr": "20:50", "duration": "1h 20m", "stops": 0},
        
        # Kööpenhamina
        {"from": "HEL", "to": "CPH", "price": 49, "airline": "SK", "dep": "07:30", "arr": "08:20", "duration": "0h 50m", "stops": 0},
        {"from": "HEL", "to": "CPH", "price": 69, "airline": "AY", "dep": "14:00", "arr": "14:50", "duration": "0h 50m", "stops": 0},
        
        # Tukholma
        {"from": "HEL", "to": "STO", "price": 45, "airline": "SK", "dep": "06:45", "arr": "07:40", "duration": "0h 55m", "stops": 0},
        {"from": "HEL", "to": "STO", "price": 55, "airline": "D8", "dep": "12:30", "arr": "13:25", "duration": "0h 55m", "stops": 0},
        
        # Teneriffa (talvimatkailu)
        {"from": "HEL", "to": "TAK", "price": 299, "airline": "AY", "dep": "10:00", "arr": "15:30", "duration": "5h 30m", "stops": 0},
        {"from": "HEL", "to": "TAK", "price": 249, "airline": "FR", "dep": "06:00", "arr": "11:40", "duration": "5h 40m", "stops": 0},
        
        # Wien
        {"from": "HEL", "to": "VIE", "price": 89, "airline": "AY", "dep": "11:00", "arr": "12:40", "duration": "1h 40m", "stops": 0},
        
        # Budapest
        {"from": "HEL", "to": "BUD", "price": 79, "airline": "W6", "dep": "18:00", "arr": "19:50", "duration": "1h 50m", "stops": 0},
        
        # Praha
        {"from": "HEL", "to": "PRG", "price": 69, "airline": "FR", "dep": "20:30", "arr": "22:00", "duration": "1h 30m", "stops": 0},
        
        # Oslo
        {"from": "HEL", "to": "OSL", "price": 55, "airline": "SK", "dep": "09:15", "arr": "10:15", "duration": "1h 00m", "stops": 0},
    ]
    
    results = demo_flights
    
    # Suodata destination mukaan
    if destination:
        results = [f for f in results if f["to"] == destination]
    
    # Suodata hinnan mukaan
    if max_price:
        results = [f for f in results if f["price"] <= max_price]
    
    # Suodata suorat lennot
    if direct_only:
        results = [f for f in results if f["stops"] == 0]
    
    return results


def format_flight(flight: Dict, dest_name: str = None) -> str:
    """Muotoile yksi lento kauniisti"""
    airline = AIRLINES.get(flight["airline"], flight["airline"])
    dest = dest_name or DESTINATIONS.get(flight["to"], flight["to"])
    
    stops_text = "suora" if flight["stops"] == 0 else f"{flight['stops']} pysähdystä"
    
    return f"""
✈️ {dest} ({flight['to']})
   {flight['dep']} → {flight['arr']} ({flight['duration']})
   {airline} | {stops_text}
   €{flight['price']}"""


def print_flights(flights: List[Dict], origin: str = "HEL"):
    """Tulosta lennot kauniisti"""
    if not flights:
        print("Ei lentoja löytynyt!")
        return
    
    print(f"\n{'='*50}")
    print(f"🇫🇮 Helsinki ({origin}) → Kohteet")
    print(f"{'='*50}")
    
    # Ryhmittele kohteen mukaan
    by_destination = {}
    for f in flights:
        key = f["to"]
        if key not in by_destination:
            by_destination[key] = []
        by_destination[key].append(f)
    
    # Tulosta
    for dest_code in sorted(by_destination.keys()):
        dest_flights = by_destination[dest_code]
        dest_name = DESTINATIONS.get(dest_code, dest_code)
        
        # Halvin lento kohteeseen
        cheapest = min(dest_flights, key=lambda x: x["price"])
        
        print(f"\n💰 {dest_name} (€{cheapest['price']})")
        print(f"   Halvin: {cheapest['dep']}→{cheapest['arr']} {cheapest['airline']}")
        
        # Muut vaihtoehdot
        if len(dest_flights) > 1:
            for f in sorted(dest_flights, key=lambda x: x["price"])[1:4]:
                print(f"   Muu:    {f['dep']}→{f['arr']} €{f['price']} {f['airline']}")


def main():
    parser = argparse.ArgumentParser(description="Lentohakusovellus")
    parser.add_argument("--from", "-f", dest="origin", default="HEL", help="Lahtoasema")
    parser.add_argument("--to", "-d", dest="destination", help="Kohde (IATA)")
    parser.add_argument("--date", help="Paiva (YYYY-MM-DD)")
    parser.add_argument("--max-price", "-p", type=float, help="Maksimihinta €")
    parser.add_argument("--direct", action="store_true", help="Vain suorat lennot")
    parser.add_argument("--demo", action="store_true", help="Nayta esimerkkidata")
    parser.add_argument("--list", action="store_true", help="Listaa kohteet")
    
    args = parser.parse_args()
    
    if args.list:
        print("Saatavilla olevat kohteet:")
        for code, name in sorted(DESTINATIONS.items()):
            print(f"  {code}: {name}")
        return
    
    # Hae lennot (mallidatasta)
    flights = get_demo_flights(
        origin=args.origin,
        destination=args.destination,
        max_price=args.max_price,
        direct_only=args.direct
    )
    
    print_flights(flights, args.origin)
    
    print(f"\n{'='*50}")
    print("HUOM: Tämä on esimerkkidata!")
    print("Oikeat lennot: rekisteröidy Amadeus/kiwi.com")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
