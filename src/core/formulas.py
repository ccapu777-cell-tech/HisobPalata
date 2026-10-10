"""Qurilish universal hisob-kitob formulalari."""

def calc_material_cost(quantity: float, unit_price: float) -> float:
    return quantity * unit_price

def calc_total_cost(quantity: float, unit_price: float, delivery: float, labor: float, extra: float) -> float:
    return (quantity * unit_price) + delivery + labor + extra

def calc_budget_remaining(budget: float, total_cost: float) -> float:
    return budget - total_cost

def calc_affordable_quantity(budget: float, unit_price: float, delivery: float, labor: float, extra: float) -> float:
    if unit_price <= 0:
        return 0.0
    net_funds = budget - delivery - labor - extra
    return max(0.0, net_funds / unit_price)