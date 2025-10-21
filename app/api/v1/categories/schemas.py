
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    slug: str = Field(min_length=2, max_length=60)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=60)
    slug: str | None = Field(default=None, min_length=2, max_length=60)


class CategoryPublic(CategoryBase):
    id: int

    model_config = {"from_attributes": True}
