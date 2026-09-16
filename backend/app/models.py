"""Pydantic models for PromptLab"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from uuid import uuid4


def generate_id() -> str:
    return str(uuid4())


def get_current_time() -> datetime:
    return datetime.utcnow()


# ============== Prompt Models ==============

class PromptBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class PromptCreate(PromptBase):
    pass


class PromptUpdate(PromptBase):
    pass

class PromptPatch(BaseModel):
    """All fields optional - only provided fields will be updated."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    tags: Optional[List[str]] = None


class Prompt(PromptBase):
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

    class Config:
        from_attributes = True

class PromptVersion(BaseModel):
    """A snapshot of a prompt's state before an update."""
    version: int
    title: str
    content: str
    description: Optional[str] = None
    collection_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    saved_at: datetime = Field(default_factory=get_current_time)    


# ============== Collection Models ==============

class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CollectionCreate(CollectionBase):
    pass


class Collection(CollectionBase):
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)

    class Config:
        from_attributes = True


# ============== Response Models ==============

class PromptList(BaseModel):
    prompts: List[Prompt]
    total: int

class PromptTestRequest(BaseModel):
    """Values to fill into a prompt template's {{variables}}."""
    variables: Dict[str, str] = Field(default_factory=dict)


class PromptTestResponse(BaseModel):
    """The prompt content with all variables replaced by values."""
    prompt_id: str
    rendered_content: str 

class VersionList(BaseModel):
    versions: List[PromptVersion]
    total: int    


class CollectionList(BaseModel):
    collections: List[Collection]
    total: int


class HealthResponse(BaseModel):
    status: str
    version: str
