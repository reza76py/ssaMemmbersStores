import math
import random
from datetime import date
from core.priority_selector import select_stores_by_priority
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    # Earth radius in kilometers
    R = 6371.0

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(R * c, 3)  # Distance in km
def generate_assignments(stores, deliveries, availability, people, visit_log):
    today = date.today()
    plan = []
    distance_details = []

    available_leaders = [p for p in availability if p["role"] == "leader" and p["available"]]
    available_members = [p for p in availability if p["role"] == "member" and p["available"]]

    if not available_leaders or not available_members:
        return [], []

    remaining_leaders = available_leaders.copy()
    remaining_members = available_members.copy()

    deliveries_sorted = sorted(deliveries, key=lambda d: d["goods_value"], reverse=True)
    deliveries_to_assign = deliveries_sorted[:len(available_leaders)]

    store_assignments = []

    for delivery in deliveries_to_assign:
        store = next((s for s in stores if s["name"] == delivery["store"]), None)
        if not store:
            continue

        sorted_leaders = sorted(
            remaining_leaders,
            key=lambda l: haversine(
                store["latitude"], store["longitude"],
                next(p["latitude"] for p in people if p["name"] == l["name"]),
                next(p["longitude"] for p in people if p["name"] == l["name"])
            )
        )

        if not sorted_leaders:
            continue

        closest_distance = haversine(
            store["latitude"], store["longitude"],
            next(p["latitude"] for p in people if p["name"] == sorted_leaders[0]["name"]),
            next(p["longitude"] for p in people if p["name"] == sorted_leaders[0]["name"])
        )
        equally_close_leaders = [l for l in sorted_leaders if 
                                 haversine(
                                     store["latitude"], store["longitude"],
                                     next(p["latitude"] for p in people if p["name"] == l["name"]),
                                     next(p["longitude"] for p in people if p["name"] == l["name"])
                                 ) == closest_distance]

        selected_leader = random.choice(equally_close_leaders)

        store_assignments.append({
            "store": store,
            "delivery": delivery,
            "leader": selected_leader,
            "assigned_members": []
        })

        remaining_leaders.remove(selected_leader)

    # ✅ Step 2: Assign 1 closest member to each leader
    for assignment in store_assignments:
        if not remaining_members:
            break

        store = assignment["store"]

        closest_member = min(
            remaining_members,
            key=lambda m: haversine(
                store["latitude"], store["longitude"],
                next(p["latitude"] for p in people if p["name"] == m["name"]),
                next(p["longitude"] for p in people if p["name"] == m["name"])
            )
        )
        assignment["assigned_members"].append(closest_member["name"])
        remaining_members.remove(closest_member)

    # ✅ Step 3: Proportional member distribution
    total_value = sum(a["delivery"]["goods_value"] for a in store_assignments)
    total_members = len(available_members)

    # Calculate how many members each store *should* get (including the one already assigned)
    store_targets = []
    for assignment in store_assignments:
        ratio = assignment["delivery"]["goods_value"] / total_value
        ideal_total = round(ratio * total_members)
        already_assigned = len(assignment["assigned_members"])
        remaining_needed = max(0, ideal_total - already_assigned)
        store_targets.append((assignment, remaining_needed))

    # Assign remaining members to closest stores needing more help
    while remaining_members and any(t[1] > 0 for t in store_targets):
        for i, (assignment, needed) in enumerate(store_targets):
            if needed == 0 or not remaining_members:
                continue

            store = assignment["store"]

            closest_member = min(
                remaining_members,
                key=lambda m: haversine(
                    store["latitude"], store["longitude"],
                    next(p["latitude"] for p in people if p["name"] == m["name"]),
                    next(p["longitude"] for p in people if p["name"] == m["name"])
                )
            )

            assignment["assigned_members"].append(closest_member["name"])
            remaining_members.remove(closest_member)
            store_targets[i] = (assignment, needed - 1)

    # ✅ Finalize plan and distances
    for assignment in store_assignments:
        store = assignment["store"]
        leader = assignment["leader"]
        members = assignment["assigned_members"]

        leader_lat = next(p["latitude"] for p in people if p["name"] == leader["name"])
        leader_lng = next(p["longitude"] for p in people if p["name"] == leader["name"])
        leader_dist = haversine(store["latitude"], store["longitude"], leader_lat, leader_lng)

        member_dists = []
        for m_name in members:
            m_lat = next(p["latitude"] for p in people if p["name"] == m_name)
            m_lng = next(p["longitude"] for p in people if p["name"] == m_name)
            m_dist = haversine(store["latitude"], store["longitude"], m_lat, m_lng)
            member_dists.append(m_dist)

        plan.append({
            "date": today.strftime("%Y-%m-%d"),
            "store": store["name"],
            "leader": leader["name"],
            "members": members
        })

        distance_details.append({
            "store": store["name"],
            "leader": leader["name"],
            "leader_travel (km)": leader_dist,
            "members": members,
            "member_travel (km)": member_dists,
            "total_travel (km)": leader_dist + sum(member_dists)
        })

    return plan, distance_details
