#!/usr/bin/env python3
"""
Testiskripti - Validoi Tilastokeskuksen API-yhteydet
"""

import requests
import sys
from typing import Tuple, Dict

BASE_URL = "https://statfin.stat.fi/PxWeb/api/v1/fi/StatFin"


def test_endpoint(table_path: str, query: dict) -> Tuple[bool, str]:
    url = f"{BASE_URL}/{table_path}"
    try:
        response = requests.post(url, json=query, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return True, f"OK ({len(data.get('data', []))} rows)"
        return False, f"Error {response.status_code}"
    except Exception as e:
        return False, str(e)[:30]


def run_tests() -> Dict[str, Tuple[bool, str]]:
    results = {}
    
    # Use JSON with proper UTF-8 characters
    tests = [
        ("rki/statfin_rki_pxt_13g8.px", {"query": [{"code": "Kuukausi", "selection": {"filter": "item", "values": ["2024M01"]}}, {"code": "Perusvuosi", "selection": {"filter": "item", "values": ["2015_100"]}}, {"code": "Tiedot", "selection": {"filter": "item", "values": ["pisteluku"]}}], "response": {"format": "json"}}, "Rakennuskustannusindeksi"),
        
        ("asvu/statfin_asvu_pxt_11x4.px", {"query": [{"code": "Vuosinelj\u00e4nnes", "selection": {"filter": "item", "values": ["2024Q1"]}}, {"code": "Alue", "selection": {"filter": "item", "values": ["ksu"]}}, {"code": "Huoneluku", "selection": {"filter": "item", "values": ["00"]}}, {"code": "Rahoitusmuoto", "selection": {"filter": "item", "values": ["0"]}}, {"code": "Tiedot", "selection": {"filter": "item", "values": ["ketj_Tor"]}}], "response": {"format": "json"}}, "Vuokraindeksi"),
        
        ("ashi/statfin_ashi_pxt_12fv.px", {"query": [{"code": "Vuosinelj\u00e4nnes", "selection": {"filter": "item", "values": ["2024Q1"]}}, {"code": "Alue", "selection": {"filter": "item", "values": ["ksu"]}}, {"code": "Talotyyppi", "selection": {"filter": "item", "values": ["0"]}}, {"code": "Huoneluku", "selection": {"filter": "item", "values": ["00"]}}, {"code": "Tiedot", "selection": {"filter": "item", "values": ["ketjutettu_lv"]}}], "response": {"format": "json"}}, "Osakeasunnot"),
        
        ("kihi/statfin_kihi_pxt_11jc.px", {"query": [{"code": "Vuosi", "selection": {"filter": "item", "values": ["2024"]}}, {"code": "Aluejako", "selection": {"filter": "item", "values": ["01"]}}, {"code": "Tiedot", "selection": {"filter": "item", "values": ["ketjutettu_lv"]}}], "response": {"format": "json"}}, "Kiinteist\u00f6jen hinnat"),
        
        ("kyki/statfin_kyki_pxt_14ry.px", {"query": [{"code": "Vuosinelj\u00e4nnes", "selection": {"filter": "item", "values": ["2024Q1"]}}, {"code": "Rakennustyyppi", "selection": {"filter": "item", "values": ["0."]}}, {"code": "Tiedot", "selection": {"filter": "item", "values": ["indeksipisteluku_kaksikatk"]}}], "response": {"format": "json"}}, "Kiinteist\u00f6n yllapito"),
        
        ("ras/statfin_ras_pxt_12fz.px", {"query": [{"code": "Kuukausi", "selection": {"filter": "item", "values": ["2024M01"]}}, {"code": "K\u00e4ytt\u00f6tarkoitus", "selection": {"filter": "item", "values": ["SSS"]}}, {"code": "Tiedot", "selection": {"filter": "item", "values": ["indeksi"]}}], "response": {"format": "json"}}, "Rakennustuotanto"),
        
        ("raku/statfin_raku_pxt_156f.px", {"query": [{"code": "rakennusvaihe", "selection": {"filter": "item", "values": ["1"]}}, {"code": "alue", "selection": {"filter": "item", "values": ["SSS"]}}, {"code": "timeperiod", "selection": {"filter": "item", "values": ["2024M01"]}}, {"code": "rakennusluokitus2018", "selection": {"filter": "item", "values": ["SSS"]}}, {"code": "ContentCode", "selection": {"filter": "item", "values": ["tilavuusToimenpide_lvs"]}}], "response": {"format": "json"}}, "Rakennusluvat"),
    ]
    
    print("="*50)
    print("TEST: Statistics Finland API endpoints")
    print("="*50)
    
    for table_path, query, desc in tests:
        print(f"{desc}...", end=" ")
        ok, msg = test_endpoint(table_path, query)
        results[desc] = (ok, msg)
        print(f"{'OK' if ok else 'FAIL'} {msg}")
    
    passed = sum(1 for ok, _ in results.values() if ok)
    print(f"\nPassed: {passed}/{len(results)}")
    return passed == len(results)


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
