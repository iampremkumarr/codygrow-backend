from pydantic import BaseModel

class CodeGenerationRequest(BaseModel):
    dataset_filename: str
    ml_type: str  # supervised / unsupervised
    task: str     # classification / regression
    model: str
    prompt: str
