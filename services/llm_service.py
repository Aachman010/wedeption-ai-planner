import json

from groq import Groq
from config import settings
from schemas.wedding import BudgetWeights


# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-20b"


def generate_budget_weights(priorities) -> BudgetWeights:

    system_prompt = """
    You are a professional wedding budget planner.

    Your task is to allocate budget weights across six categories
    based on the priorities provided by the user.

    Categories:
    - venue
    - catering
    - decoration
    - photography
    - entertainment
    - miscellaneous

    Example of the expected output format:

    {
        "venue": 0.25,
        "catering": 0.25,
        "decoration": 0.15,
        "photography": 0.15,
        "entertainment": 0.10,
        "miscellaneous": 0.10
    }

    Follow these rules:

    1. High-priority categories should receive relatively higher weights.
    2. Medium-priority categories should receive moderate weights.
    3. Low-priority categories should receive relatively lower weights.
    4. Allocate a reasonable weight to miscellaneous.
    5. All six weights must be between 0 and 1.
    6. The sum of all six weights must equal 1.0.
    7. Return only the JSON object.
    8. Do not include explanations, Markdown, or code fences.

    The example demonstrates the format only.
    Do not copy its values blindly.
    Generate weights according to the user's priorities.
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": json.dumps(priorities)
            }
        ],
        temperature=0.2,
        max_completion_tokens=1500,
        reasoning_effort="low")
    llm_output = response.choices[0].message.content

    if not llm_output:
      raise ValueError("LLM returned an empty response.")

    # 3. Convert JSON string into Python dictionary
    weights_dict = json.loads(llm_output)

    total_weight = sum(weights_dict.values())

    if total_weight <= 0:
       raise ValueError("Total weight must be greater than zero")

    weights_dict = {
    category: weight / total_weight
    for category, weight in weights_dict.items()
     }

    print(weights_dict)
    print("Total weight:", sum(weights_dict.values()))


    # 4. Validate dictionary using Pydantic
    validated_weights = BudgetWeights.model_validate(weights_dict)
  

    # 5. Return Pydantic object
    return validated_weights
    


    
import json

def get_llm_response(final_dict):

    system_prompt = """
    You are a professional wedding planner.

    Your task is to generate a personalized, detailed wedding plan
    using the information provided by the user.

    STRICT RULES:

    1. Use only the vendor names and prices provided in the input.
    2. Do not invent vendors, prices, services, or budget figures.
    3. Do not modify the category budgets calculated by Python.
    4. Do not recalculate or redistribute the budget.
    5. The sum of category budgets must remain unchanged.
    6. If information is missing, do not make up values.
    7. Keep the plan practical and within the given total budget.

    FORMAT YOUR RESPONSE USING THESE SECTIONS:

    # Wedding Plan

    ## 1. Wedding Overview
    Mention city, total budget, guest count, and wedding duration.

    ## 2. Category-wise Wedding Plan
    For each category, mention:
    - Allocated budget
    - Selected vendor name
    - Vendor price
    - Services or details provided in the input

    ## 3. Budget Summary
    Show a clear table containing:
    - Category
    - Allocated budget
    - Selected vendor
    - Vendor cost

    ## 4. Recommendations
    Provide practical suggestions based on the provided information.

    ## 5. Final Note
    Give a short concluding recommendation.

    IMPORTANT:
    Preserve all numerical values exactly as provided.
    Return only the wedding plan in readable Markdown.
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": json.dumps(final_dict, ensure_ascii=False)
            }
        ],
        temperature=0.2,
        max_completion_tokens=3000,
        reasoning_effort="low"
    )

    llm_output = response.choices[0].message.content

    if not llm_output:
        raise ValueError("LLM returned an empty response.")

    return llm_output