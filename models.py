from pydantic import BaseModel, Field


class UserQuery(BaseModel):
    user_id: str = Field(min_length=1, max_length=64, pattern="^[a-zA-Z0-9_-]+$")

    model_config = {"extra": "forbid"}