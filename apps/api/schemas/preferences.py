from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list[JsonScalar] | dict[str, JsonScalar]


class Preference(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "intended_major": "Computer Science",
                "home_state": "CA",
                "max_annual_cost": 32000,
                "weights": {"academic": 0.25, "cost": 0.25, "career": 0.25, "campus": 0.25},
                "constraints": {"region": "West"},
            }
        }
    )

    intended_major: str | None = None
    home_state: str | None = Field(default=None, min_length=2, max_length=2)
    max_annual_cost: int | None = Field(default=None, ge=0)
    weights: dict[str, float] = Field(default_factory=dict)
    constraints: dict[str, JsonValue] = Field(default_factory=dict)
