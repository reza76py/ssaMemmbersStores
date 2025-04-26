import math
from datetime import date

def calculate_distance(lat1, lng1, lat2, lng2):
    return math.sqrt((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2)

def generate_assignments(stores, deliveries, availability, people):
    today = date.today()
    plan = []

    available_leaders = [p for p in availability if p["role"] == "leader" and p["available"]]
    available_members = [p for p in availability if p["role"] == "member" and p["available"]]

    for i, delivery in enumerate(deliveries):
        store = next((s for s in stores if s["name"] == delivery["store"]), None)
        if not store:
            continue

        value = delivery["goods_value"]
        num_members = 1 if value <= 5000 else 2 if value <= 10000 else 3

        # Find closest leader
        leader = min(
            available_leaders,
            key=lambda l: calculate_distance(
                store["latitude"], store["longitude"],
                next(p["latitude"] for p in people if p["name"] == l["name"]),
                next(p["longitude"] for p in people if p["name"] == l["name"])
            )
        )

        # Find closest members
        sorted_members = sorted(
            available_members,
            key=lambda m: calculate_distance(
                store["latitude"], store["longitude"],
                next(p["latitude"] for p in people if p["name"] == m["name"]),
                next(p["longitude"] for p in people if p["name"] == m["name"])
            )
        )
        assigned_members = sorted_members[:num_members]

        plan.append({
            "date": date(today.year, today.month, today.day + (i % 3)).strftime("%Y-%m-%d"),
            "store": store["name"],
            "leader": leader["name"],
            "members": [m["name"] for m in assigned_members]
        })

    return plan
