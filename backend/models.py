from pydantic import BaseModel

class RegisterRequest(BaseModel):
    email: str

class UploadRequest(BaseModel):
    file_name: str
    file_data: bytes
