
from schemas.wedding import BudgetWeights


def calculate_budget(
    total_budget: float,
    baseline_data: dict,
    weights: BudgetWeights
):

    # Extract the minimum cost for each vendor category
    baseline_costs = {
        category: data["baseline_cost"]
        for category, data in baseline_data.items()
    }

    # Miscellaneous is not a vendor category
    # Its baseline allocation is currently zero
    baseline_costs["miscellaneous"] = 0

    # Calculate total minimum required budget
    minimum_total = sum(baseline_costs.values())

    if minimum_total > total_budget:
        raise ValueError(
            "Total budget is insufficient for the minimum wedding requirements."
        )

    # Money remaining after covering minimum vendor costs
    remaining_budget = total_budget - minimum_total

    weights_dict = weights.model_dump()

    final_budget = {}

    for category, weight in weights_dict.items():

        baseline_cost = baseline_costs.get(category, 0)

        additional_amount = remaining_budget * weight

        final_budget[category] = round(
            baseline_cost + additional_amount
        )

    # Correct any rounding difference so total allocation
    # equals the original total budget
    difference = total_budget - sum(final_budget.values())

    if difference != 0:
        final_budget["miscellaneous"] += difference

    return final_budget
