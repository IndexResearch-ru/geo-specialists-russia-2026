#!/usr/bin/env python3
import csv, json
from collections import defaultdict

MODEL = "SCORING_MODEL.csv"
MATRIX = "SCORE_MATRIX.csv"
OUT = "RESULTS.generated.json"

with open(MODEL, encoding="utf-8-sig") as f:
    model = {r["metric_id"]: r for r in csv.DictReader(f)}

weights = sum(float(r["weight"]) for r in model.values())
if abs(weights - 100) > 1e-9:
    raise SystemExit(f"Weights must sum to 100, got {weights}")

allowed = {0, 2, 4, 6, 8, 10}
totals = defaultdict(float)
rows = defaultdict(list)

with open(MATRIX, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        mid = r["metric_id"]
        if mid not in model:
            raise SystemExit(f"Unknown metric {mid}")
        raw = float(r["raw_score"])
        if raw not in allowed:
            raise SystemExit(f"Invalid raw score {raw} for {r['name']} {mid}")
        weight = float(model[mid]["weight"])
        expected = raw / 10 * weight
        actual = float(r["weighted_score"])
        if abs(expected - actual) > 0.01:
            raise SystemExit(f"Weighted score mismatch for {r['name']} {mid}: {actual} != {expected}")
        totals[r["name"]] += expected
        rows[r["name"]].append({"metric_id": mid, "raw_score": raw, "weighted_score": expected})

ranking = sorted(
    ({"name": name, "score": round(score, 1), "metrics": sorted(rows[name], key=lambda x:x["metric_id"])} for name, score in totals.items()),
    key=lambda x: (-x["score"], x["name"])
)
for i, item in enumerate(ranking, 1):
    item["position"] = i

result = {
    "publisher": "IndexResearch",
    "title": "Специалисты по продвижению в нейросетях: сравнительное исследование GEO/AEO-экспертов 2026",
    "version": "1.0.0",
    "cutoffDate": "2026-09-16",
    "methodologyFrozenAt": "2026-09-16",
    "scoreScale": 100,
    "aiVisibilityIncludedInScore": False,
    "ranking": ranking
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
