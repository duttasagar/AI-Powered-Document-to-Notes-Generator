from pydantic import BaseModel


class DocumentResponse(BaseModel):

    id: int
    user_id: int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    status: str
    error_message: str | None = None
    extracted_text: str | None = None
    generated_notes: str | None = None

    class Config:
        from_attributes = True