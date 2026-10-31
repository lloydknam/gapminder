#!/usr/bin/env python3
"""OECD(지표) + World Bank(X축 GDP, 크기 인구) -> data/*.json  (OECD 38개국만)"""
import csv, io, json, re, sys, urllib.request, urllib.error, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data"; OUT.mkdir(exist_ok=True)
COUNTRIES = list(json.load(open(ROOT / "countries.json")))
cat = json.load(open(ROOT / "indicators.json"))

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gapminder-sample"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read().decode("utf-8-sig")
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode("utf-8", "replace")[:300]
        except Exception: pass
        raise RuntimeError(f"HTTP {e.code} {url[:140]} :: {body}") from None

def quality(d):
    """국가 30개 이상, 연도 10개 이상, 한국 값 존재"""
    ys = {y for c in d.values() for y in c}
    return len(d) >= 30 and len(ys) >= 10 and "KOR" in d

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

DIAG = {}
def oecd_flow(flow, inds):
    """한 flow를 한 번만 내려받아 해당 flow의 모든 지표를 동시에 처리 -> {id: data | Exception}"""
    st = {i["id"]: {"vals": {}, "seen": {}, "combo": {}} for i in inds}
    for r in opencsv(flow, 1990):
        c = r["REF_AREA"]
        if c not in COUNTRIES or not r["OBS_VALUE"]: continue
        for ind in inds:
            if r.get("FREQ", "A") != ind.get("freq", "A"): continue
            S = st[ind["id"]]
            if ind.get("suffix") and not r["TIME_PERIOD"].endswith(ind["suffix"]): continue
            for k in ind["filters"]: S["seen"].setdefault(k, set()).add(r.get(k))
            fk = list(ind["filters"])
            if r.get(fk[0]) == ind["filters"][fk[0]] and len(S["combo"]) < 600:
                ck = tuple(r.get(k) for k in fk); S["combo"][ck] = S["combo"].get(ck, 0) + 1
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
        DIAG[ind["id"]] = {"conflict": conflict, "keys": list(ind["filters"]), "top_combos": sorted(([list(k), n] for k, n in S["combo"].items()), key=lambda x: -x[1])[:25]}
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

DBN = "https://api.db.nomics.world/v22"   # IMF WEO는 DBnomics(공개 API) 경유
WEO_DS = None
def dbn_dataset():
    global WEO_DS
    if WEO_DS: return WEO_DS
    docs, off = [], 0
    while True:
        res = None
        for lim in ("limit=100&", "limit=50&", ""):
            try: res = json.loads(get(f"{DBN}/datasets/IMF?{lim}offset={off}")); break
            except RuntimeError as e: err = e
        if res is None: raise err
        d = res["datasets"]; docs += d["docs"]; off += len(d["docs"])
        if not d["docs"] or off >= d.get("num_found", 0): break
    res = {"datasets": {"docs": docs}}
    names = [d["code"] for d in res["datasets"]["docs"]]
    pd = OUT / "_probe"; pd.mkdir(exist_ok=True)
    json.dump({d["code"]: d.get("name") for d in res["datasets"]["docs"]}, open(pd / "imf_datasets.json", "w"), ensure_ascii=False, indent=0)
    weo = sorted(n for n in names if re.fullmatch(r"WEO:\d{4}-\d{2}", n))
    if not weo: raise RuntimeError(f"WEO 데이터셋 없음: {names[:30]}")
    WEO_DS = weo[-1]; print("WEO 데이터셋", WEO_DS)
    try:
        info = json.loads(get(f"{DBN}/datasets/IMF/{WEO_DS}"))["datasets"]["docs"][0]
        json.dump({"dimensions_labels": info.get("dimensions_labels"), "dimensions_values_labels": info.get("dimensions_values_labels")}, open(pd / "imf_catalog.json", "w"), ensure_ascii=False, indent=0)
    except BaseException as e: print("[WEO 카탈로그 실패]", e)
    return WEO_DS
def imf(code, mult=1):
    import urllib.parse
    ds = dbn_dataset(); d = {}; seen = 0; raw = []
    off = 0; LIM = 1000
    while off < 8000:
        try: j = json.loads(get(f"{DBN}/series/IMF/{ds}?q={urllib.parse.quote(code)}&observations=1&limit={LIM}&offset={off}"))["series"]
        except RuntimeError as e:
            if LIM > 100: LIM = 100; continue
            raise
        for doc in j["docs"]:
            dims = doc.get("dimensions", {}); vs = list(dims.values())
            if code not in vs: continue
            c = next((v for v in vs if v in COUNTRIES), None)
            if len(raw) < 3: raw.append({k: doc.get(k) for k in ("series_code", "dimensions", "period", "value")})
            if not c: continue
            for per, v in zip(doc.get("period", []), doc.get("value", [])):
                if isinstance(v, (int, float)) and int(str(per)[:4]) >= 1990: d.setdefault(c, {})[str(per)[:4]] = v * mult
        seen += len(j["docs"]); off += LIM
        if off >= j.get("num_found", 0) or not j["docs"]: break
    if not d:
        pd = OUT / "_probe"; pd.mkdir(exist_ok=True); json.dump(raw, open(pd / f"dbn_{code}.json", "w"), ensure_ascii=False, indent=0)
        raise RuntimeError(f"DBnomics에서 {code} 시리즈를 찾지 못함 (검색 {seen}건)")
    return d

save(cat["x"]["id"], worldbank(cat["x"]["wb"]))
save(cat["size"]["id"], worldbank(cat["size"]["wb"]))
ok, flows, probes, wbs, imfs = [], {}, [], [], []
FAIL = {}
def note(k, m):
    FAIL[k] = str(m)[:3500]; json.dump(FAIL, open(OUT / "failures.json", "w"), ensure_ascii=False, indent=1)
for c in cat["categories"]:
    for ind in c["indicators"]:
        if ind["status"] == "ready" and ind.get("imf"): imfs.append(ind)
        elif ind["status"] == "ready" and ind.get("wb"): wbs.append(ind)
        elif ind["status"] == "ready": flows.setdefault(ind["flow"], []).append(ind)
        elif ind["status"] == "probe": probes.append(ind)
for flow, inds in flows.items():
    try:
        res = oecd_flow(flow, inds)
    except BaseException as e:
        print(f"[실패] {flow}: {type(e).__name__} {e}", flush=True); note(flow, f"{type(e).__name__} {e}"); continue
    for ind in inds:
        r = res[ind["id"]]
        if isinstance(r, Exception): print(f"[실패] {ind['id']}: {r}", flush=True); note(ind["id"], str(r) + " | DIAG " + json.dumps(DIAG.get(ind["id"]), ensure_ascii=False))
        elif not quality(r): print(f"[품질미달] {ind['id']}: {len(r)}개국, 연도 {len({y for c in r.values() for y in c})}개, KOR={'KOR' in r}"); note(ind["id"], f"품질미달: {len(r)}개국, 연도 {len({y for c in r.values() for y in c})}개, KOR={'KOR' in r} | DIAG " + json.dumps(DIAG.get(ind["id"]), ensure_ascii=False))
        else: save(ind["id"], r); ok.append(ind["id"])
    json.dump(ok, open(OUT / "ready.json", "w"))
for ind in wbs:
    try:
        tries = [(ind["wb"], ind.get("wbsrc")), (ind["wb"], None)] + ([(ind["wbalt"], None)] if ind.get("wbalt") else [])
        for k, (cd, sr) in enumerate(tries):
            try:
                r = worldbank(cd, ind.get("mult", 1), sr); break
            except Exception as e:
                print(f"  [재시도 {cd} src={sr}] {e}", flush=True)
                if k == len(tries) - 1: raise
        if not quality(r): print(f"[품질미달] {ind['id']}: {len(r)}개국, 연도 {len({y for c in r.values() for y in c})}개, KOR={'KOR' in r}"); note(ind["id"], "품질미달")
        else: save(ind["id"], r); ok.append(ind["id"])
        import time; time.sleep(0.7)
    except BaseException as e:
        print(f"[실패] {ind['id']} ({ind['wb']}): {type(e).__name__} {e}", flush=True); note(ind["id"], f"{type(e).__name__} {e}")
    json.dump(ok, open(OUT / "ready.json", "w"))
for ind in imfs:
    try:
        r = imf(ind["imf"], ind.get("mult", 1))
        if not quality(r): print(f"[품질미달] {ind['id']}: {len(r)}개국, 연도 {len({y for c in r.values() for y in c})}개, KOR={'KOR' in r}"); note(ind["id"], f"품질미달: {len(r)}개국, KOR={'KOR' in r}")
        else: save(ind["id"], r); ok.append(ind["id"])
        import time; time.sleep(0.5)
    except BaseException as e:
        print(f"[실패] {ind['id']} (IMF {ind['imf']}): {type(e).__name__} {e}", flush=True); note(ind["id"], f"{type(e).__name__} {e}")
    json.dump(ok, open(OUT / "ready.json", "w"))
for ind in probes:
    try: probe(ind)
    except BaseException as e: print(f"[probe실패] {ind['id']}: {type(e).__name__} {e}", flush=True)
json.dump(ok, open(OUT / "ready.json", "w"))
print("완료:", ok)

import datetime
_n = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
json.dump({"updated": _n.strftime("%Y-%m-%d"), "proj_from": int(WEO_DS[4:8]) if WEO_DS else (_n.year if _n.month >= 4 else _n.year - 1)}, open(OUT / "meta.json", "w"))
