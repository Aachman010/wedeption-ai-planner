from pydantic import BaseModel, Field,model_validator
from typing import Literal
from typing import Any


class WeddingRequest(BaseModel):#response sent by the client
    city: str
    total_budget: float = Field(gt=10000)
    guest_count: int = Field(gt=0)
    wedding_days: int = Field(ge=1, le=10)

    photography_priority: Literal["low", "medium", "high"]
    entertainment_priority: Literal["low", "medium", "high"]
    decoration_priority: Literal["low", "medium", "high"]
    catering_priority: Literal["low", "medium", "high"]
    venue_priority: Literal["low", "medium", "high"]

class BudgetWeights(BaseModel):#weights send by the llm(validates the model o/p)
    venue: float = Field(ge=0, le=1)
    catering: float = Field(ge=0, le=1)
    decoration: float = Field(ge=0, le=1)
    photography: float = Field(ge=0, le=1)
    entertainment: float = Field(ge=0, le=1)
    miscellaneous: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_total_weight(self):
        total = sum(self.model_dump().values())

        if abs(total - 1.0) > 1e-6:
            raise ValueError("Budget weights must sum to 1.0")

        return self

class BudgetCalculationRequest(BaseModel):#test the calculate budget fucntion independent of llm
    total_budget: float = Field(gt=0)
    weights: BudgetWeights


class BudgetCalculationResponse(BaseModel):#model response ko validate krega are the each category budgets correct
    venue: float = Field(ge=0)
    catering: float = Field(ge=0)
    decoration: float = Field(ge=0)
    photography: float = Field(ge=0)
    entertainment: float = Field(ge=0)
    miscellaneous: float = Field(ge=0)

class WeddingPlanResponse(BaseModel):
    city:str
    total_budget:float
    category_budgets:BudgetCalculationResponse
    vendors: dict[str,list[dict[str,Any]]]





