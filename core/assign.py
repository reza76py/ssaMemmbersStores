import math
import random
from datetime import date
from core.priority_selector import select_stores_by_priority

def calculate_distance(lat1, lng1, lat2, lng2):
    return round(math.sqrt((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2), 2)

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
            key=lambda l: calculate_distance(
                store["latitude"], store["longitude"],
                next(p["latitude"] for p in people if p["name"] == l["name"]),
                next(p["longitude"] for p in people if p["name"] == l["name"])
            )
        )

        if not sorted_leaders:
            continue

        closest_distance = calculate_distance(
            store["latitude"], store["longitude"],
            next(p["latitude"] for p in people if p["name"] == sorted_leaders[0]["name"]),
            next(p["longitude"] for p in people if p["name"] == sorted_leaders[0]["name"])
        )
        equally_close_leaders = [l for l in sorted_leaders if 
                                 calculate_distance(
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

    # Step 2: Guarantee at least 1 member
    for assignment in store_assignments:
        if not remaining_members:
            break

        store = assignment["store"]

        sorted_members = sorted(
            remaining_members,
            key=lambda m: calculate_distance(
                store["latitude"], store["longitude"],
                next(p["latitude"] for p in people if p["name"] == m["name"]),
                next(p["longitude"] for p in people if p["name"] == m["name"])
            )
        )

        if sorted_members:
            selected_member = sorted_members[0]
            assignment["assigned_members"].append(selected_member["name"])
            remaining_members.remove(selected_member)

    # Step 3: Distribute remaining members
    for assignment in sorted(store_assignments, key=lambda a: a["delivery"]["goods_value"], reverse=True):
        if not remaining_members:
            break

        store = assignment["store"]
        delivery = assignment["delivery"]

        value = delivery["goods_value"]
        total_members_needed = 1 if value <= 5000 else 2 if value <= 10000 else 3
        already_assigned = len(assignment["assigned_members"])
        still_needed = total_members_needed - already_assigned

        if still_needed <= 0:
            continue

        sorted_members = sorted(
            remaining_members,
            key=lambda m: calculate_distance(
                store["latitude"], store["longitude"],
                next(p["latitude"] for p in people if p["name"] == m["name"]),
                next(p["longitude"] for p in people if p["name"] == m["name"])
            )
        )

        assigned_now = sorted_members[:still_needed]
        for m in assigned_now:
            assignment["assigned_members"].append(m["name"])
            remaining_members.remove(m)

    # Step 4: Build final outputs
    for assignment in store_assignments:
        store = assignment["store"]
        leader = assignment["leader"]
        members = assignment["assigned_members"]

        # Leader distance
        leader_lat = next(p["latitude"] for p in people if p["name"] == leader["name"])
        leader_lng = next(p["longitude"] for p in people if p["name"] == leader["name"])
        leader_dist = calculate_distance(store["latitude"], store["longitude"], leader_lat, leader_lng)

        # Members distances
        member_dists = []
        for m_name in members:
            m_lat = next(p["latitude"] for p in people if p["name"] == m_name)
            m_lng = next(p["longitude"] for p in people if p["name"] == m_name)
            m_dist = calculate_distance(store["latitude"], store["longitude"], m_lat, m_lng)
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
            "leader_distance": leader_dist,
            "members": members,
            "member_distances": member_dists,
            "total_distance": leader_dist + sum(member_dists)
        })

    return plan, distance_details
