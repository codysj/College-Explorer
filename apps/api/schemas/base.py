from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    """Base for every request and response schema.

    Responses serialize every field, defaults included, so the response half of the
    OpenAPI schema marks defaulted fields required. Without this the generated frontend
    types would make them optional and every consumer would have to handle `undefined`
    for values the API always sends.
    """

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)
