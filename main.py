
from fastapi import FastAPI, HTTPException,Path
from fastapi.responses import FileResponse

from schemas.wedding import WeddingRequest
from services.vendor_service import calculate_baseline_costs
from services.budget_service import calculate_budget
from services.llm_service import generate_budget_weights, get_llm_response

import json

app = FastAPI(
    title="AI Wedding Planner",
    description="AI-powered wedding budget and vendor planning API",
    version="1.0.0"
)
@app.get("/")
def serve_frontend():
    #frontend_path = Path(__file__).parent / "wedplan_frontend.html"
    return FileResponse('wedplan_frontend.html')

def generate_wedding_plan(request: WeddingRequest):

    # 1. Calculate baseline costs and retrieve eligible vendors
    baseline_data = calculate_baseline_costs(
        wedding_request=request
    )

    # 2. Prepare priorities
    priorities = {
        "venue": request.venue_priority,
        "catering": request.catering_priority,
        "decoration": request.decoration_priority,
        "photography": request.photography_priority,
        "entertainment": request.entertainment_priority
    }

    # 3. Generate budget weights using the LLM
    weights = generate_budget_weights(priorities)

    # 4. Allocate the total budget
    calculated_budget = calculate_budget(
        total_budget=request.total_budget,
        baseline_data=baseline_data,
        weights=weights
    )

    # 5. Filter vendors according to allocated budgets
    category_details = {}

    for category, budget in calculated_budget.items():

        vendor_info = baseline_data.get(category, {})

        eligible_vendors = vendor_info.get(
            "eligible_vendors", []
        )

        suitable_vendors = [
            vendor
            for vendor in eligible_vendors
            if vendor["estimated_cost"] <= budget
        ]

        category_details[category] = {
            "allocated_budget": budget,
            "baseline_cost": vendor_info.get("baseline_cost", 0),
            "baseline_vendor": vendor_info.get("baseline_vendor"),
            "suitable_vendors": suitable_vendors
        }

    # 6. Prepare data for the final LLM
    final_dict = {
        "city": request.city,
        "total_budget": request.total_budget,
        "guest_count": request.guest_count,
        "wedding_days": request.wedding_days,
        "category_details": category_details
    }

    print("DATA SENT TO LLM:")
    print(json.dumps(final_dict, indent=4, ensure_ascii=False))

    # 7. Generate final wedding plan
    llm_output = get_llm_response(final_dict)

    return {
        "wedding_plan": llm_output
    }


@app.post("/generate-wedding-plan")
def create_wedding_plan(request: WeddingRequest):

    try:
        return generate_wedding_plan(request)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print(f"Error generating wedding plan: {error}")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating the wedding plan."
        )
