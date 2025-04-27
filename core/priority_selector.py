from core.priority import calculate_store_priorities

def select_stores_by_priority(stores, visit_log, deliveries_today, limit):
    """
    Select 'limit' number of stores to visit based on highest priority.
    Only stores with deliveries today are considered.
    """

    # Get store priorities
    priority_list = calculate_store_priorities(stores, visit_log)

    # Filter priority list to only stores that have deliveries today
    delivery_store_names = [d["store"] for d in deliveries_today]
    filtered_priority = [store for store in priority_list if store["Store"] in delivery_store_names]

    # Pick top N stores
    top_stores = filtered_priority[:limit]

    return [store["Store"] for store in top_stores]
