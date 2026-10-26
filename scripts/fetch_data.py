#!/usr/bin/env python3
"""OECD(지표) + World Bank(X축 GDP, 크기 인구) -> data/*.json  (OECD 38개국만)"""
import csv, io, json, sys, urllib.request, urllib.error, pathlib
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

def worldbank(code, mult=1, src=None):
    import time
    url = f"https://api.worldbank.org/v2/country/{';'.join(COUNTRIES)}/indicator/{code}?format=json&per_page=20000&date=1990:2030" + (f"&source={src}" if src else "")
    for att in range(3):
        res = json.loads(get(url))
        if len(res) >= 2 and res[1]: break
        time.sleep(3 * (att + 1))
    else:
        raise RuntimeError(f"세계은행 지표 없음/빈 응답: {res[0] if res else res}")
    d = {}
    for r in res[1]:
        if r["value"] is not None:
            d.setdefault(r["countryiso3code"], {})[r["date"]] = r["value"] * mult
    return d

def opencsv(flow, start):
    import time
    url = f"https://sdmx.oecd.org/public/rest/data/{flow}/all?startPeriod={start}&format=csvfile"
    for att in range(1, 6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "gapminder-sample"})
            resp = urllib.request.urlopen(req, timeout=600)
            return csv.DictReader(io.TextIOWrapper(resp, encoding="utf-8-sig", newline=""))
        except urllib.error.HTTPError as e:
            if e.code != 429 or att == 5: raise
            print(f"  429 재시도 {att}", flush=True); time.sleep(60 * att)

def oecd_flow(flow, inds):
    """한 flow를 한 번만 내려받아 해당 flow의 모든 지표를 동시에 처리 -> {id: data | Exception}"""
    st = {i["id"]: {"vals": {}, "seen": {}} for i in inds}
    for r in opencsv(flow, 1990):
        c = r["REF_AREA"]
        if c not in COUNTRIES or not r["OBS_VALUE"]: continue
        for ind in inds:
            if r.get("FREQ", "A") != ind.get("freq", "A"): continue
            S = st[ind["id"]]
            if ind.get("suffix") and not r["TIME_PERIOD"].endswith(ind["suffix"]): continue
            for k in ind["filters"]: S["seen"].setdefault(k, set()).add(r.get(k))
            if any(r.get(k) != v for k, v in ind["filters"].items()): continue
            pref = ind.get("prefer")
            S["vals"].setdefault((c, r["TIME_PERIOD"][:4]), []).append((r.get(pref, "") if pref else "", float(r["OBS_VALUE"]) * ind.get("mult", 1)))
    out = {}
    for ind in inds:
        S, d, conflict = st[ind["id"]], {}, 0
        for (c, y), L in S["vals"].items():
            if ind.get("prefer"): v = max(L)[1]
            elif len({x[1] for x in L}) == 1: v = L[0][1]
            else: conflict += 1; continue
            d.setdefault(c, {})[y] = v
        if conflict: print(f"  경고 {ind['id']}: 중복값 충돌 {conflict}건 제외")
        out[ind["id"]] = d if d else RuntimeError("필터 결과 없음. 실제 값: " + str({k: sorted(map(str, v))[:40] for k, v in S["seen"].items()}))
    return out

def probe(ind):
    url = f"https://sdmx.oecd.org/public/rest/data/{ind['flow']}/all?startPeriod=2015&format=csvfile"
    rd = opencsv(ind["flow"], 2015)
    uniq, n = {}, 0
    for r in rd:
        if any(r.get(k) != v for k, v in ind.get("filters", {}).items()): continue
        n += 1
        for k, v in r.items():
            if k in ("OBS_VALUE", "TIME_PERIOD", "REF_AREA", "STRUCTURE", "STRUCTURE_ID", "STRUCTURE_NAME", "ACTION"): continue
            u = uniq.setdefault(k, set())
            if len(u) <= 300: u.add(v)
    pd = OUT / "_probe"; pd.mkdir(exist_ok=True)
    json.dump({"rows": n, "values": {k: sorted(v) for k, v in uniq.items() if len(v) > 1 or k in ("FREQ", "UNIT_MEASURE", "MEASURE")}}, open(pd / f"{ind['id']}.json", "w"), ensure_ascii=False)
    print("probe", ind["id"], n)

save(cat["x"]["id"], worldbank(cat["x"]["wb"]))
save(cat["size"]["id"], worldbank(cat["size"]["wb"]))
ok, flows, probes, wbs = [], {}, [], []
for c in cat["categories"]:
    for ind in c["indicators"]:
        if ind["status"] == "ready" and ind.get("wb"): wbs.append(ind)
        elif ind["status"] == "ready": flows.setdefault(ind["flow"], []).append(ind)
        elif ind["status"] == "probe": probes.append(ind)
for flow, inds in flows.items():
    try:
        res = oecd_flow(flow, inds)
    except BaseException as e:
        print(f"[실패] {flow}: {type(e).__name__} {e}", flush=True); continue
    for ind in inds:
        r = res[ind["id"]]
        if isinstance(r, Exception): print(f"[실패] {ind['id']}: {r}", flush=True)
        else: save(ind["id"], r); ok.append(ind["id"])
    json.dump(ok, open(OUT / "ready.json", "w"))
for ind in wbs:
    try:
        save(ind["id"], worldbank(ind["wb"], ind.get("mult", 1), ind.get("wbsrc"))); ok.append(ind["id"])
        import time; time.sleep(0.7)
    except BaseException as e:
        print(f"[실패] {ind['id']} ({ind['wb']}): {type(e).__name__} {e}", flush=True)
    json.dump(ok, open(OUT / "ready.json", "w"))
for ind in probes:
    try: probe(ind)
    except BaseException as e: print(f"[probe실패] {ind['id']}: {type(e).__name__} {e}", flush=True)
json.dump(ok, open(OUT / "ready.json", "w"))
print("완료:", ok)
