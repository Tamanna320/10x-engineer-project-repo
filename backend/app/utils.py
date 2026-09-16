"""Utility functions for PromptLab"""

from typing import List, Dict
from app.models import Prompt


def sort_prompts_by_date(prompts: List[Prompt], descending: bool = True) -> List[Prompt]:
    """Sort prompts by creation date.
    
    descending=True  -> newest first
    descending=False -> oldest first
    """
    return sorted(prompts, key=lambda p: p.created_at, reverse=descending)


def filter_prompts_by_collection(prompts: List[Prompt], collection_id: str) -> List[Prompt]:
    return [p for p in prompts if p.collection_id == collection_id]

def filter_prompts_by_tag(prompts: List[Prompt], tag: str) -> List[Prompt]:
    """Keep only prompts that have the given tag."""
    return [p for p in prompts if tag in p.tags]

def search_prompts(prompts: List[Prompt], query: str) -> List[Prompt]:
    query_lower = query.lower()
    return [
        p for p in prompts 
        if query_lower in p.title.lower() or 
           (p.description and query_lower in p.description.lower())
    ]


def validate_prompt_content(content: str) -> bool:
    """Check if prompt content is valid.
    
    A valid prompt should:
    - Not be empty
    - Not be just whitespace
    - Be at least 10 characters
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10


def extract_variables(content: str) -> List[str]:
    """Extract template variables from prompt content.
    
    Variables are in the format {{variable_name}}
    """
    import re
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)

def render_prompt(content: str, variables: Dict[str, str]) -> str:
    """Replace every {{variable}} in content with its provided value."""
    rendered = content
    for name, value in variables.items():
        rendered = rendered.replace("{{" + name + "}}", value)
    return rendered