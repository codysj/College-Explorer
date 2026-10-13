import json
from typing import Annotated, TypeAlias

from pydantic import ConfigDict, Field, model_validator

from schemas.base import ApiModel
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list[JsonScalar] | dict[str, JsonScalar]


class Preference(ApiModel):
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

    intended_major: str | None = Field(default=None, max_length=120)
    home_state: str | None = Field(default=None, min_length=2, max_length=2)
    max_annual_cost: int | None = Field(default=None, ge=0, le=250_000)
    weights: dict[Annotated[str, Field(max_length=40)], Annotated[float, Field(ge=0, le=100)]] = Field(
        default_factory=dict, max_length=16
    )
    constraints: dict[Annotated[str, Field(max_length=40)], JsonValue] = Field(default_factory=dict, max_length=16)

    @model_validator(mode="after")
    def bound_constraint_size(self) -> "Preference":
        # Constraint values are free-form JSON; cap the whole object rather than each shape.
        if len(json.dumps(self.constraints, default=str)) > 2048:
            raise ValueError("constraints may be at most 2 KB when serialized")
        return self
