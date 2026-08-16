from pydantic import BaseModel


class RunbookResult(BaseModel):
    title: str
    source: str
    content: str
