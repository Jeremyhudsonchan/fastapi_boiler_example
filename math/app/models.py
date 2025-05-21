from pydantic import BaseModel, Field

class MathInput(BaseModel):
    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")

class OperationResult(BaseModel):
    operation: str
    a: float
    b: float
    result: float
