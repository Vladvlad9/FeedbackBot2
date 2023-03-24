from datetime import datetime
from pydantic import BaseModel, Field


class ApplicantFormSchema(BaseModel):
    phone_number: str = Field(min_length=12, max_length=12, default=None)
    is_published: bool = Field(default=True)
    date_created: datetime = Field(default=datetime.now())
    name: str
    surname: str
    user_id: int = Field(ge=1)


class ApplicantFormInDBSchema(ApplicantFormSchema):
    id: int = Field(ge=1)
