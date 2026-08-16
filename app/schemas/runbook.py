from datetime import datetime

from pydantic import BaseModel


class RunbookResult(BaseModel):
    title: str
    source: str
    content: str


class RunbookCatalogResponse(BaseModel):
    title: str
    source: str
    chunks: int
    last_indexed: datetime
    content: str
    index_status: str = "INDEXED"
