#!/usr/bin/env python3
"""OECD 데이터플로우 목록 + 후보 플로우의 차원값 요약 -> data/_discovery/"""
import csv, io, json, re, sys, time, urllib.request, pathlib
import xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "_discovery"; OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://sdmx.oecd.org/public/rest/"
KEYS = ["life expectancy","health expenditure","health spending","hospital beds","physicians","nurses","infant mortality","avoidable mortality","obesity","smoking","alcohol",
 "productivity","gdp per capita","unemployment","employment rate","average annual wages","average wage","hours worked","minimum wage","collective bargaining","trade union",
 "tax revenue","revenue statistics","government debt","general government","tax wedge","social expenditure","public pension","pension","old-age dependency","fertility","migration",
 "income distribution","gini","poverty","inequality","r&d","research and development","patent","tertiary","pisa","education at a glance","educational attainment","greenhouse","co2","air pollution","renewable","energy","municipal waste","internet","broadband","national accounts","population"]
def get(u, retry=3):
    for i in range(retry):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "gapminder-sample"})
            return urllib.request.urlopen(req, timeout=180).read().decode("utf-8-sig")
        except Exception as e:
            err = e; time.sleep(5 * (i + 1))
    raise err
x = get(BASE + "dataflow/all?detail=allstubs")
flows = []
for el in ET.fromstring(x).iter():
    if el.tag.endswith("}Dataflow"):
        nm = next((c.text for c in el if c.tag.endswith("}Name") and c.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") == "en"), "")
        flows.append((el.attrib["agencyID"], el.attrib["id"], el.attrib["version"], nm))
(OUT / "dataflows.tsv").write_text("\n".join("\t".join(f) for f in flows))
print(len(flows), "dataflows")
cand = [f for f in flows if any(k in f[3].lower() for k in KEYS)]
print(len(cand), "candidates")
summ = {}
for ag, id_, ver, nm in cand:
    key = f"{ag},{id_},{ver}"
    try:
        t = get(BASE + f"data/{key}/all?lastNObservations=1&dimensionAtObservation=AllDimensions&format=csvfilewithlabels")
        rows = list(csv.DictReader(io.StringIO(t)))
    except Exception as e:
        summ[key] = {"name": nm, "error": str(e)[:100]}; print("ERR", key, e); continue
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
    print("ok", key, nm, len(rows)); time.sleep(1)
json.dump(summ, open(OUT / "flows_summary.json", "w"), ensure_ascii=False, indent=1)
