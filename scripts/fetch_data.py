#!/usr/bin/env python3
"""OECD(지표) + World Bank(X축 GDP, 크기 인구) -> data/*.json  (OECD 38개국만)"""
import csv, io, json, sys, urllib.request, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data"; OUT.mkdir(exist_ok=True)
COUNTRIES = list(json.load(open(ROOT / "countries.json")))
cat = json.load(open(ROOT / "indicators.json"))

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gapminder-sample"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8-sig")

def save(name, d):
    json.dump(d, open(OUT / f"{name}.json", "w"), separators=(",", ":"))
    print(f"saved {name}: {len(d)} countries")

def worldbank(code):
    url = f"https://api.worldbank.org/v2/country/{';'.join(COUNTRIES)}/indicator/{code}?format=json&per_page=20000&date=1990:2030"
    meta, rows = json.loads(get(url))
    d = {}
    for r in rows:
        if r["value"] is not None:
            d.setdefault(r["countryiso3code"], {})[r["date"]] = r["value"]
    return d

def oecd(ind):
    url = f"https://sdmx.oecd.org/public/rest/data/{ind['flow']}/all?startPeriod=1990&format=csvfilewithlabels"
    rd = csv.DictReader(io.StringIO(get(url)))
    vals, seen = {}, {}
    pref = ind.get("prefer")
    for r in rd:
        for k in ind["filters"]:
            seen.setdefault(k, set()).add(r.get(k))
        if any(r.get(k) != v for k, v in ind["filters"].items()): continue
        c = r["REF_AREA"]
        if c not in COUNTRIES or r.get("FREQ", "A") != "A" or not r["OBS_VALUE"]: continue
        vals.setdefault((c, r["TIME_PERIOD"][:4]), []).append((r.get(pref, "") if pref else "", float(r["OBS_VALUE"])))
    d, conflict = {}, 0
    for (c, y), L in vals.items():
        if pref: v = max(L)[1]
        elif len({x[1] for x in L}) == 1: v = L[0][1]
        else: conflict += 1; continue
        d.setdefault(c, {})[y] = v
    if conflict: print(f"  경고: 중복값 충돌 {conflict}건 제외")
    if not d:
        raise RuntimeError("필터 결과 없음. 실제 값: " + str({k: sorted(map(str, v))[:40] for k, v in seen.items()}))
    return d

save(cat["x"]["id"], worldbank(cat["x"]["wb"]))
save(cat["size"]["id"], worldbank(cat["size"]["wb"]))
ok = []
for c in cat["categories"]:
    for ind in c["indicators"]:
        if ind["status"] != "ready": continue
        try:
            save(ind["id"], oecd(ind)); ok.append(ind["id"])
        except Exception as e:
            print(f"[실패] {ind['id']}: {e}")
json.dump(ok, open(OUT / "ready.json", "w"))
print("완료:", ok)
