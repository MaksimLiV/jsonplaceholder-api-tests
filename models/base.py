from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """Base for every response model.

    - extra="forbid": a new or renamed field in the API fails the test (schema drift).
    - strict=True: "1" is not accepted where an int is expected.
    - alias_generator: Python uses user_id, the API uses userId.
    """

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        alias_generator=to_camel,
    )
