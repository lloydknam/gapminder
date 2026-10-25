#!/usr/bin/env python3
"""OECD 데이터플로우 목록 + 후보 플로우의 차원값 요약 -> data/_discovery/"""
import csv, io, json, re, sys, time, urllib.request, urllib.error, pathlib
import xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "_discovery"; OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://sdmx.oecd.org/public/rest/"
KEYS = ["life expectancy","health expenditure","health spending","hospital beds","physicians","nurses","infant mortality","avoidable mortality","obesity","smoking","alcohol",
 "labour productivity","productivity levels","unemployment rate","employment rate","employment-population","average annual wages","hours worked","minimum wage","collective bargaining","trade union","union density",
 "revenue statistics","government debt","general government debt","taxing wages","tax wedge","social expenditure","public pension","pension","old-age","dependency ratio","fertility","net migration","international migration",
 "income distribution","poverty","gini","inequality","research and development","gross domestic expenditure on r&d","main science and technology","patent","tertiary","pisa","education at a glance","educational attainment","greenhouse","co2","air pollution","renewable","municipal waste","broadband","national accounts","gdp per capita","population"]
EXCL = ["regions","region ","cities","fuas","local areas","africa","asia and the pacific","latin america","tax and non-tax","subnational","municipal level","territorial","provinces","county"]
def get(u, retry=6):
    for i in range(retry):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "gapminder-sample"})
            return urllib.request.urlopen(req, timeout=180).read().decode("utf-8-sig")
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (404, 413): raise
            time.sleep(60 * (i + 1) if e.code == 429 else 10)
        except Exception as e:
            err = e; time.sleep(10)
    raise err
x = get(BASE + "dataflow/all?detail=allstubs")
flows = []
for el in ET.fromstring(x).iter():
    if el.tag.endswith("}Dataflow"):
        nm = next((c.text for c in el if c.tag.endswith("}Name") and c.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") == "en"), "")
        flows.append((el.attrib["agencyID"], el.attrib["id"], el.attrib["version"], nm))
(OUT / "dataflows.tsv").write_text("\n".join("\t".join(f) for f in flows))
print(len(flows), "dataflows")
cand = [f for f in flows if any(k in f[3].lower() for k in KEYS) and not any(x in f[3].lower() for x in EXCL)]
print(len(cand), "candidates", flush=True)
(OUT / "candidates.tsv").write_text("\n".join("\t".join(f) for f in cand))
summ = {}
for ag, id_, ver, nm in cand:
    key = f"{ag},{id_},{ver}"
    try:
        t = get(BASE + f"data/{key}/all?lastNObservations=1&dimensionAtObservation=AllDimensions&format=csvfilewithlabels")
        rows = list(csv.DictReader(io.StringIO(t)))
    except Exception as e:
        summ[key] = {"name": nm, "error": str(e)[:100]}; print("ERR", key, e, flush=True); time.sleep(3); continue
    cols = {}
    for c in rows[0].keys() if rows else []:
        if c in ("OBS_VALUE", "TIME_PERIOD", "REF_AREA") or c.endswith(": Reference area") : continue
        vals = {}
        for r in rows:
            vals.setdefault(r[c], 0); vals[r[c]] += 1
        if len(vals) <= 40: cols[c] = sorted(vals)
        else: cols[c] = f"{len(vals)} values"
    ca = {r.get("REF_AREA") for r in rows}
    ty = sorted({r.get("TIME_PERIOD", "") for r in rows})
    summ[key] = {"name": nm, "rows": len(rows), "countries": len(ca), "latest_periods": ty[-3:], "columns": cols}
    print("ok", key, nm, len(rows), flush=True); time.sleep(3)
    json.dump(summ, open(OUT / "flows_summary.json", "w"), ensure_ascii=False, indent=1)
json.dump(summ, open(OUT / "flows_summary.json", "w"), ensure_ascii=False, indent=1)
