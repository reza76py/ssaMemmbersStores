from datetime import datetime, date

def calculate_store_priorities(stores, visit_log):
    priority_data = []

    for store in stores:
        store_name = store["name"]

        visits = [v for v in visit_log if v["store"] == store_name]

        if visits:
            last_visit_str = max(v["date"] for v in visits)
            last_visit = datetime.strptime(last_visit_str, "%Y-%m-%d").date()
            days_since = (date.today() - last_visit).days
        else:
            last_visit = None
            days_since = 999  # Never visited = highest priority

        priority_data.append({
            "Store": store_name,
            "Last Visit": last_visit.strftime("%Y-%m-%d") if last_visit else "Never",
            "Days Since Last": days_since,
            "Priority Score": days_since
        })

    # High to low priority
    return sorted(priority_data, key=lambda x: x["Priority Score"], reverse=True)
