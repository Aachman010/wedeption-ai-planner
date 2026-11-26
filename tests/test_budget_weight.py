from services.llm_service import generate_budget_weights
from services.vendor_service import calculate_baseline_costs
from services.budget_service import calculate_budget
from schemas.wedding import WeddingRequest


# 1. Create wedding request object
wedding_request = WeddingRequest(
    city="Bhopal",
    total_budget=1000000,
    guest_count=300,
    wedding_days=2,
    venue_priority="high",
    catering_priority="high",
    decoration_priority="medium",
    photography_priority="high",
    entertainment_priority="low"
)


# 2. Extract priorities
priorities = {
    "venue": wedding_request.venue_priority,
    "catering": wedding_request.catering_priority,
    "decoration": wedding_request.decoration_priority,
    "photography": wedding_request.photography_priority,
    "entertainment": wedding_request.entertainment_priority
}


# 3. Generate weights using LLM
weights = generate_budget_weights(priorities)


# 4. Calculate baseline vendor data
baseline_data = calculate_baseline_costs(wedding_request)


# 5. Add miscellaneous baseline
baseline_data["miscellaneous"] = {
    "baseline_vendor": None,
    "baseline_cost": 0
}


# 6. Calculate final budget
final_budget = calculate_budget(
    wedding_request.total_budget,
    baseline_data,
    weights
)


# 7. Display results
print("\nBASELINE DATA:")
print(baseline_data)

print("\nLLM WEIGHTS:")
print(weights.model_dump())

print("\nFINAL BUDGET:")
print(final_budget)

print("\nTOTAL ALLOCATED:")
print(sum(final_budget.values()))