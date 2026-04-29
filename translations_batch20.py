"""Batch 20 — final missed player-visible strings (Tohta intro + quote)."""
import csv

T = {
    "I expect his voice to emerge as a rasp, but instead it spills like silk from behind his crystalline mask. There is a purity to the sound of him; every word reaches me as cleanly as a whisper in the ear.":
        "Mi aspetto che la sua voce emerga come un raschio, ma invece scorre come seta da dietro la sua maschera cristallina. C'è una purezza nel suono che produce; ogni parola mi raggiunge nitida come un sussurro all'orecchio.",
    '<<"Isn’t it a wonder? We turned a bane into a boon, and a boon into a culture. All the chemicals and coincidences that conspired to create the Crystal Farmers.">>':
        '<<"Non è una meraviglia? Abbiamo trasformato una rovina in una benedizione, e una benedizione in una cultura. Tutte le sostanze chimiche e le coincidenze che hanno cospirato per creare i Coltivatori di Cristalli.">>',
}

CSV_PATH = "translations/ink_strings.csv"

rows = []
with open(CSV_PATH, encoding="utf-8") as f:
    r = csv.reader(f)
    header = next(r)
    for row in r:
        rows.append(row)

applied = 0
for row in rows:
    if len(row) >= 3 and row[2].strip() == "" and row[1] in T:
        row[2] = T[row[1]]
        applied += 1

with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(rows)

translated = sum(1 for row in rows if len(row) >= 3 and row[2].strip())
print(f"Applied {applied} new translations from this batch")
print(f"Total translated: {translated}/{len(rows)}")
