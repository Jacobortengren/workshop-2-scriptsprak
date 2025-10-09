### DEL A ###
### Task 1: Läs in CSV-filen med csv.DictReader ###
import csv

# Öppnar CSV-filen och läser in varje rad som en ordbok (dict)
with open("network_incidents.csv", encoding="utf-8") as f:
    incidents = list(csv.DictReader(f))

### Task 2: Visa kontorsnamn och analysperiod från datan ###

# Hämta alla sites och veckonummer
sites = sorted(set(row["site"] for row in incidents))
weeks = [int(row["week_number"]) for row in incidents]

print("Offices:")
for site in sites:
    print(f"- {site}")

print("-------------------------------------------------------------------------------------------------")
print(f"Analysis period: Week {min(weeks)} - {max(weeks)}")

### Task 3: Räkna totalt antal incidents per severity-nivå (critical, high, medium, low) ###
print("-------------------------------------------------------------------------------------------------")
from collections import Counter

# Räknar hur många incidenter det finns av varje severity-nivå
severity_count = Counter(row["severity"].lower() for row in incidents)
print("Total incidents per severity level:")
for severity in ["critical", "high", "medium", "low"]:
    print(f"- {severity.capitalize()}: {severity_count.get(severity, 0)}")

### Task 4: Lista alla incidents som påverkade fler än 100 användare ###

def safe_int(s):
    if not s:
        return 0
    return int(s)

print("-------------------------------------------------------------------------------------------------")
print("Incidents that affected more than 100 users:\n")
# Loopa igenom alla incidenter och filtrera ut de som påverkat fler än 100 användare
for row in incidents:
    affected = safe_int(row.get("affected_users"))
    if affected > 100:
        print(f"- Ticket: {row['ticket_id']}, Site: {row['site']}, Severity: {row['severity']}, Affected users: {affected}")
print("-------------------------------------------------------------------------------------------------")

### Task 5: Identifiera de 5 dyraste incidenterna (kräver svenska kostnadsformat parsing) ###

# Funktion som konverterar kostnader från svenskt format (med kommatecken) till float
def parse_cost(cost_str):
    # Tar bort mellanslag och ersätter komma med punkt
    if not cost_str:
        return 0.0
    clean = cost_str.replace(" ", "").replace(",", ".")
    return float(clean)

# Sorterar incidenter efter kostnad i fallande ordning och tar ut topp 5
top5 = sorted(incidents, key=lambda r: parse_cost(r["cost_sek"]), reverse=True)[:5]

print("The 5 most expensive incidents:\n")
# Skriver ut de fem dyraste incidenterna
for row in top5:
    cost = parse_cost(row["cost_sek"])
    print(f"- Ticket: {row['ticket_id']}, Site: {row['site']}, Severity: {row['severity']}, Cost: {cost} SEK")

### DEL B ###
### Task 6 : Beräkna total kostnad för alla incidents ###

# Summerar alla kostnader
total_cost = sum(parse_cost(row["cost_sek"]) for row in incidents)
print("-------------------------------------------------------------------------------------------------")
print(f"Total cost for all incidents: {total_cost:.2f} SEK")

### Task 7: Genomsnittlig resolution time (minuter) per severity-nivå ###
from collections import defaultdict

# Skapar en struktur för att lagra resolution-tider per severity
resolution_times = defaultdict(list)

# Samlar in resolution_minutes per severity-nivå
for row in incidents:
    severity = row["severity"].lower()
    try:
        minutes = int(row["resolution_minutes"])
    except:
        minutes = 0
    resolution_times[severity].append(minutes)

print("-------------------------------------------------------------------------------------------------")
print("Average resolution time per severity level:")
# Räknar och skriver ut genomsnittlig resolution time för varje nivå
for severity in ["critical", "high", "medium", "low"]:
    times = resolution_times.get(severity, [])
    avg = sum(times) / len(times) if times else 0
    print(f"- {severity.capitalize()}: {avg:.1f} minutes")

### Task 8: Skapa en översikt per site (antal incidents, total kostnad, genomsnittliga resolution minuter) ###
from collections import defaultdict

# Samlar in data per site: antal incidenter, total kostnad och resolution-tider
site_data = defaultdict(lambda: {"count": 0, "total_cost": 0.0, "resolution_times": []})

for row in incidents:
    site = row["site"]
    site_data[site]["count"] += 1
    site_data[site]["total_cost"] += parse_cost(row["cost_sek"])
    try:
        site_data[site]["resolution_times"].append(int(row["resolution_minutes"]))
    except:
        site_data[site]["resolution_times"].append(0)

print("-------------------------------------------------------------------------------------------------")
print("Overview per site:")
# Skriver ut statistik per site
for site, data in site_data.items():
    avg_resolution = sum(data["resolution_times"]) / len(data["resolution_times"]) if data["resolution_times"] else 0
    print(f"- Site: {site}")
    print(f"  Number of incidents: {data['count']}")
    print(f"  Total cost: {data['total_cost']:.2f} SEK")
    print(f"  Average resolution time: {avg_resolution:.1f} minutes\n")

### Task 9: Lista incidents per kategori med genomsnittlig impact score ###
from collections import defaultdict

# Skapar en struktur för att samla data per kategori
category_data = defaultdict(lambda: {"count": 0, "impact_scores": []})

# Hämtar och konverterar impact score till float (hanterar svenska kommatecken)
for row in incidents:
    category = row["category"]
    try:
        impact = float(row["impact_score"].replace(",", "."))
    except:
        impact = 0.0
    category_data[category]["count"] += 1
    category_data[category]["impact_scores"].append(impact)

print("-------------------------------------------------------------------------------------------------")
print("Average impact score per category:")
# Beräknar och skriver ut genomsnittlig impact score per kategori
for category, data in category_data.items():
    avg_impact = sum(data["impact_scores"]) / len(data["impact_scores"]) if data["impact_scores"] else 0
    print(f"- {category}: {avg_impact:.2f} (number of incidents: {data['count']})")

### Task 10: Skapa CSV-fil "incidents_by_site.csv" med sammanfattning per lokation ###
import csv

# Skapar en sammanställning av incidents per site
site_summary = {}

for row in incidents:
    site = row["site"]
    cost = parse_cost(row.get("cost_sek", "0"))
    resolution = float(row.get("resolution_minutes", 0))  # <-- korrekt kolumnnamn

    if site not in site_summary:
        site_summary[site] = {"incidents": 0, "total_cost": 0, "total_resolution": 0}

    site_summary[site]["incidents"] += 1
    site_summary[site]["total_cost"] += cost
    site_summary[site]["total_resolution"] += resolution

# Beräknar genomsnittlig resolution-tid per site
for site in site_summary:
    total = site_summary[site]
    total["avg_resolution"] = total["total_resolution"] / total["incidents"]

# Skriver ut sammanställningen till en ny CSV-fil
with open("incidents_by_site.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["site", "incidents", "total_cost_SEK", "avg_resolution_minutes"])
    for site, data in site_summary.items():
        writer.writerow([
            site,
            data["incidents"],
            f"{data['total_cost']:.2f}",
            f"{data['avg_resolution']:.2f}"
        ])

print("-------------------------------------------------------------------------------------------------")
print("The file 'incidents_by_site.csv' has been created with summary per site.")
