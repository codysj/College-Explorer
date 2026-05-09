from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SchoolSort = Literal[
    "name",
    "acceptance_rate",
    "graduation_rate",
    "net_price",
    "undergraduate_enrollment",
]
SortDirection = Literal["asc", "desc"]


class SchoolSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unitid: int
    name: str
    city: str
    state: str
    region: str
    type: str
    setting: str
    undergraduate_enrollment: int | None = None
    acceptance_rate: float | None = None


class SchoolProfile(BaseModel):
    school: SchoolSummary
    top_majors: list[str] = Field(default_factory=list)
    graduation_rate: float | None = None
    net_price: int | None = None
    median_earnings: int | None = None
    campus_tags: list[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    region: str | None = Field(default=None, max_length=32)
    type: str | None = Field(default=None, max_length=32)
    setting: str | None = Field(default=None, max_length=32)
    min_enrollment: int | None = Field(default=None, ge=0)
    max_enrollment: int | None = Field(default=None, ge=0)
    max_net_price: int | None = Field(default=None, ge=0)
    max_acceptance_rate: float | None = Field(default=None, ge=0, le=1)
    min_graduation_rate: float | None = Field(default=None, ge=0, le=1)
    sort: SchoolSort = "name"
    direction: SortDirection = "asc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchResponse(BaseModel):
    results: list[SchoolSummary] = Field(default_factory=list)
    page: int = 1
    page_size: int = 20
    total_results: int = 0
    has_next: bool = False
