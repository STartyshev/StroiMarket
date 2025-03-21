from pydantic import BaseModel, ConfigDict


class ImageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    image_link: str


class ProductSubtypeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    name: str


class ProductTypeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    name: str
    product_subtypes: list["ProductSubtypeDTO"]


class ProductCardDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    name: str
    price: float
    image_link: str
    rating: float
