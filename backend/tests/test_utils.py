"""Unit tests for the utility functions in app/utils.py.

Covers sort_prompts_by_date, filter_prompts_by_collection,
filter_prompts_by_tag, search_prompts, validate_prompt_content,
extract_variables, and render_prompt.
"""

import pytest

from app.models import Prompt
from app.utils import (
    sort_prompts_by_date,
    filter_prompts_by_collection,
    filter_prompts_by_tag,
    search_prompts,
    validate_prompt_content,
    extract_variables,
    render_prompt,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def make_prompt(title="Test", content="Content", description=None, tags=None, collection_id=None):
    """Create a Prompt with sensible defaults."""
    return Prompt(
        title=title,
        content=content,
        description=description,
        tags=tags or [],
        collection_id=collection_id,
    )


# ============================================================
# sort_prompts_by_date
# ============================================================

class TestSortPromptsByDate:
    """Tests for sorting prompts by creation date."""

    def test_sort_descending_newest_first(self):
        p1 = make_prompt(title="First")
        p2 = make_prompt(title="Second")
        p3 = make_prompt(title="Third")
        # Give them different created_at values
        p1.created_at = "2025-01-01T00:00:00"
        p2.created_at = "2025-01-02T00:00:00"
        p3.created_at = "2025-01-03T00:00:00"

        result = sort_prompts_by_date([p1, p2, p3], descending=True)
        assert result[0].title == "Third"
        assert result[1].title == "Second"
        assert result[2].title == "First"

    def test_sort_ascending_oldest_first(self):
        p1 = make_prompt(title="First")
        p2 = make_prompt(title="Second")
        p1.created_at = "2025-01-01T00:00:00"
        p2.created_at = "2025-01-02T00:00:00"

        result = sort_prompts_by_date([p2, p1], descending=False)
        assert result[0].title == "First"
        assert result[1].title == "Second"

    def test_sort_does_not_modify_input(self):
        p1 = make_prompt(title="A")
        p2 = make_prompt(title="B")
        p1.created_at = "2025-01-01T00:00:00"
        p2.created_at = "2025-01-02T00:00:00"
        original = [p1, p2]

        sort_prompts_by_date(original)
        assert original[0] is p1
        assert original[1] is p2

    def test_sort_empty_list(self):
        assert sort_prompts_by_date([]) == []


# ============================================================
# filter_prompts_by_collection
# ============================================================

class TestFilterPromptsByCollection:
    """Tests for filtering prompts by collection ID."""

    def test_returns_matching_prompts(self):
        p1 = make_prompt(title="A", collection_id="col-1")
        p2 = make_prompt(title="B", collection_id="col-2")
        p3 = make_prompt(title="C", collection_id="col-1")

        result = filter_prompts_by_collection([p1, p2, p3], "col-1")
        assert len(result) == 2
        assert p1 in result
        assert p3 in result

    def test_returns_empty_when_no_match(self):
        p1 = make_prompt(title="A", collection_id="col-1")
        result = filter_prompts_by_collection([p1], "col-99")
        assert result == []

    def test_excludes_prompts_with_none_collection(self):
        p1 = make_prompt(title="A", collection_id=None)
        result = filter_prompts_by_collection([p1], "col-1")
        assert result == []


# ============================================================
# filter_prompts_by_tag
# ============================================================

class TestFilterPromptsByTag:
    """Tests for filtering prompts by tag."""

    def test_returns_matching_prompts(self):
        p1 = make_prompt(title="A", tags=["python", "beginner"])
        p2 = make_prompt(title="B", tags=["cooking"])

        result = filter_prompts_by_tag([p1, p2], "python")
        assert len(result) == 1
        assert result[0] is p1

    def test_returns_empty_when_no_match(self):
        p1 = make_prompt(title="A", tags=["python"])
        result = filter_prompts_by_tag([p1], "nonexistent")
        assert result == []

    def test_case_sensitive_match(self):
        p1 = make_prompt(title="A", tags=["Python"])
        result = filter_prompts_by_tag([p1], "python")
        assert result == []


# ============================================================
# search_prompts
# ============================================================

class TestSearchPrompts:
    """Tests for searching prompts by title or description."""

    def test_match_in_title_case_insensitive(self):
        p1 = make_prompt(title="Write an Email", content="C")
        result = search_prompts([p1], "email")
        assert len(result) == 1
        assert result[0] is p1

    def test_match_in_description(self):
        """A query that matches the description (but not the title) should return the prompt."""
        p1 = make_prompt(title="Recipe", content="C", description="A pasta cooking guide")
        result = search_prompts([p1], "pasta")
        assert len(result) == 1
        assert result[0] is p1

    def test_description_none_does_not_crash(self):
        """A prompt with description=None should not raise and should only match on title."""
        p1 = make_prompt(title="Hello World", content="C", description=None)
        # Match on title — should return the prompt
        result = search_prompts([p1], "hello")
        assert len(result) == 1
        assert result[0] is p1

        # No match on title — should return empty (description=None is skipped)
        result = search_prompts([p1], "nonexistent")
        assert result == []

    def test_empty_query_matches_all(self):
        p1 = make_prompt(title="A", content="C")
        p2 = make_prompt(title="B", content="C")
        result = search_prompts([p1, p2], "")
        assert len(result) == 2

    def test_no_match_returns_empty(self):
        p1 = make_prompt(title="Hello", content="C", description="World")
        result = search_prompts([p1], "xyz")
        assert result == []


# ============================================================
# validate_prompt_content
# ============================================================

class TestValidatePromptContent:
    """Tests for validating prompt content."""

    def test_valid_content(self):
        assert validate_prompt_content("Summarize this text.") is True

    def test_valid_content_with_surrounding_whitespace(self):
        """Content that is long enough after stripping should be valid."""
        assert validate_prompt_content("   Summarize this text.   ") is True

    def test_empty_string_returns_false(self):
        assert validate_prompt_content("") is False

    def test_only_whitespace_returns_false(self):
        assert validate_prompt_content("       ") is False

    def test_short_content_returns_false(self):
        """Content shorter than 10 characters (after stripping) is invalid."""
        assert validate_prompt_content("short") is False

    def test_content_exactly_10_chars_is_valid(self):
        assert validate_prompt_content("1234567890") is True

    def test_content_9_chars_is_invalid(self):
        assert validate_prompt_content("123456789") is False


# ============================================================
# extract_variables
# ============================================================

class TestExtractVariables:
    """Tests for extracting template variables from content."""

    def test_extract_single_variable(self):
        assert extract_variables("Hello {{name}}!") == ["name"]

    def test_extract_multiple_variables(self):
        result = extract_variables("Write a {{tone}} email to {{name}}.")
        assert result == ["tone", "name"]

    def test_no_variables_returns_empty(self):
        assert extract_variables("No variables here") == []

    def test_duplicate_variables_returned_per_occurrence(self):
        result = extract_variables("{{name}} and {{name}}")
        assert result == ["name", "name"]

    def test_variable_with_underscore_and_digits(self):
        result = extract_variables("{{user_1}} and {{code_42}}")
        assert result == ["user_1", "code_42"]


# ============================================================
# render_prompt
# ============================================================

class TestRenderPrompt:
    """Tests for rendering prompt templates with variable values."""

    def test_render_single_variable(self):
        result = render_prompt("Hello {{name}}!", {"name": "Ada"})
        assert result == "Hello Ada!"

    def test_render_multiple_variables(self):
        result = render_prompt(
            "Write a {{tone}} email to {{name}}.",
            {"tone": "friendly", "name": "Bob"},
        )
        assert result == "Write a friendly email to Bob."

    def test_missing_variable_placeholder_left_unchanged(self):
        """A placeholder with no matching key should remain in the output."""
        result = render_prompt("Hello {{name}} from {{city}}!", {"name": "Ada"})
        assert result == "Hello Ada from {{city}}!"

    def test_extra_keys_have_no_effect(self):
        """Keys without a matching placeholder do nothing."""
        result = render_prompt("Hello {{name}}!", {"name": "Ada", "unused": "x"})
        assert result == "Hello Ada!"

    def test_no_variables_returns_original(self):
        result = render_prompt("No placeholders", {})
        assert result == "No placeholders"
