"""Utility functions for PromptLab"""


from app.models import Prompt


def sort_prompts_by_date(prompts: list[Prompt], descending: bool = True) -> list[Prompt]:
    """Sort prompts by creation date.

    Returns a new list; the input list is not modified.

    Args:
        prompts: The prompts to sort.
        descending: If True, sort newest first (default).
            If False, sort oldest first.

    Returns:
        A new list of prompts sorted by their ``created_at`` timestamp.

    Examples:
        >>> sort_prompts_by_date(prompts)  # newest first
        >>> sort_prompts_by_date(prompts, descending=False)  # oldest first
    """
    return sorted(prompts, key=lambda p: p.created_at, reverse=descending)


def filter_prompts_by_collection(prompts: list[Prompt], collection_id: str) -> list[Prompt]:
    """Keep only prompts that belong to the given collection.

    Args:
        prompts: The prompts to filter.
        collection_id: The collection ID to match exactly
            against each prompt's ``collection_id``.

    Returns:
        A new list containing only prompts whose ``collection_id``
        equals the given value. Empty if no prompts match.

    Examples:
        >>> filter_prompts_by_collection(prompts, "col-123")
    """
    return [p for p in prompts if p.collection_id == collection_id]

def filter_prompts_by_tag(prompts: list[Prompt], tag: str) -> list[Prompt]:
    """Keep only prompts that have the given tag.

    Matching is an exact membership test against each prompt's
    ``tags`` list (case-sensitive).

    Args:
        prompts: The prompts to filter.
        tag: The tag to look for in each prompt's ``tags``.

    Returns:
        A new list containing only prompts that include ``tag``
        in their ``tags``. Empty if no prompts match.

    Examples:
        >>> filter_prompts_by_tag(prompts, "marketing")
    """
    return [p for p in prompts if tag in p.tags]

def search_prompts(prompts: list[Prompt], query: str) -> list[Prompt]:
    """Search prompts by title or description (case-insensitive).

    A prompt matches if the lowercased query is a substring of its
    lowercased title, or of its lowercased description when the
    description is set (a ``None`` or empty description is skipped).
    An empty query matches every prompt.

    Args:
        prompts: The prompts to search.
        query: The search text. Matched case-insensitively as a
            substring, not as a whole word.

    Returns:
        A new list of matching prompts. Empty if nothing matches.

    Examples:
        >>> search_prompts(prompts, "Email")  # matches "Write an email"
    """
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
    - Be at least 10 characters (after stripping surrounding whitespace)

    Args:
        content: The prompt content to validate.

    Returns:
        True if the content, once stripped, is at least 10 characters
        long; False if it is empty, only whitespace, or too short.

    Examples:
        >>> validate_prompt_content("Summarize this text.")
        True
        >>> validate_prompt_content("   ")
        False
        >>> validate_prompt_content("short")
        False
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10


def extract_variables(content: str) -> list[str]:
    """Extract template variables from prompt content.

    Variables are in the format ``{{variable_name}}``, where the name
    consists of one or more word characters (letters, digits, underscore).
    A variable that appears multiple times is returned once per occurrence;
    names are not deduplicated.

    Args:
        content: The prompt content to scan for variables.

    Returns:
        A list of variable names (without the surrounding braces) in
        order of appearance. Empty if the content has no variables.

    Examples:
        >>> extract_variables("Write a {{tone}} email to {{name}}.")
        ['tone', 'name']
    """
    import re
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)

def render_prompt(content: str, variables: dict[str, str]) -> str:
    """Replace every ``{{variable}}`` in content with its provided value.

    Substitution is a plain string replacement for each entry in
    ``variables``. Placeholders without a matching key are left
    unchanged, and keys with no matching placeholder have no effect.

    Args:
        content: The prompt content containing ``{{variable}}``
            placeholders.
        variables: Mapping of variable names (without braces) to the
            values that should replace them.

    Returns:
        The rendered content with all provided variables substituted.

    Examples:
        >>> render_prompt("Hello {{name}}!", {"name": "Ada"})
        'Hello Ada!'
    """
    rendered = content
    for name, value in variables.items():
        rendered = rendered.replace("{{" + name + "}}", value)
    return rendered