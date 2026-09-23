"""Unit tests for the Storage class in app/storage.py.

Covers prompt CRUD, collection CRUD, get_prompts_by_collection(),
version operations, missing-entity cases, clear(), and consistency
after create/update/delete cycles.
"""

import pytest

from app.models import Prompt, Collection, PromptVersion
from app.storage import Storage


# ------------------------------------------------------------------
# Helper factory functions — keep tests short and readable
# ------------------------------------------------------------------

def make_prompt(title="Test Prompt", content="Test content", collection_id=None):
    """Create a Prompt with sensible defaults."""
    return Prompt(title=title, content=content, collection_id=collection_id)


def make_collection(name="Test Collection", description=None):
    """Create a Collection with sensible defaults."""
    return Collection(name=name, description=description)


def make_version(version, title="Old Title", content="Old content"):
    """Create a PromptVersion with sensible defaults."""
    return PromptVersion(version=version, title=title, content=content)


@pytest.fixture
def store():
    """Provide a fresh, isolated Storage instance for every test."""
    return Storage()


# ============================================================
# Prompt CRUD
# ============================================================

class TestPromptCRUD:
    """Tests for create, get, get_all, update, and delete on prompts."""

    def test_create_prompt(self, store):
        prompt = make_prompt(title="My Prompt")
        result = store.create_prompt(prompt)
        assert result is prompt
        # The stored prompt should be retrievable by its id
        assert store.get_prompt(prompt.id) is prompt

    def test_create_prompt_overwrites_existing_id(self, store):
        original = make_prompt(title="Original")
        store.create_prompt(original)
        # Creating with the same id overwrites
        replacement = Prompt(id=original.id, title="Replacement", content="New")
        store.create_prompt(replacement)
        stored = store.get_prompt(original.id)
        assert stored.title == "Replacement"

    def test_get_prompt_returns_none_when_missing(self, store):
        assert store.get_prompt("nonexistent-id") is None

    def test_get_all_prompts_empty(self, store):
        assert store.get_all_prompts() == []

    def test_get_all_prompts_returns_all(self, store):
        p1 = make_prompt(title="A")
        p2 = make_prompt(title="B")
        store.create_prompt(p1)
        store.create_prompt(p2)
        all_prompts = store.get_all_prompts()
        assert len(all_prompts) == 2
        assert p1 in all_prompts
        assert p2 in all_prompts

    def test_get_all_prompts_returns_copy(self, store):
        """get_all_prompts returns a new list, not the internal dict values."""
        p1 = make_prompt(title="A")
        store.create_prompt(p1)
        first_call = store.get_all_prompts()
        second_call = store.get_all_prompts()
        assert first_call == second_call
        assert first_call is not second_call

    def test_update_prompt_existing(self, store):
        prompt = make_prompt(title="Original")
        store.create_prompt(prompt)
        updated = Prompt(id=prompt.id, title="Updated", content="New content")
        result = store.update_prompt(prompt.id, updated)
        assert result is updated
        assert store.get_prompt(prompt.id).title == "Updated"

    def test_update_prompt_returns_none_when_missing(self, store):
        updated = make_prompt(title="Updated")
        assert store.update_prompt("nonexistent-id", updated) is None

    def test_delete_prompt_existing(self, store):
        prompt = make_prompt()
        store.create_prompt(prompt)
        assert store.delete_prompt(prompt.id) is True
        assert store.get_prompt(prompt.id) is None

    def test_delete_prompt_missing_returns_false(self, store):
        assert store.delete_prompt("nonexistent-id") is False

    def test_delete_prompt_also_removes_versions(self, store):
        prompt = make_prompt()
        store.create_prompt(prompt)
        store.save_version(prompt.id, make_version(1))
        store.delete_prompt(prompt.id)
        assert store.get_versions(prompt.id) == []


# ============================================================
# Collection CRUD
# ============================================================

class TestCollectionCRUD:
    """Tests for create, get, get_all, and delete on collections."""

    def test_create_collection(self, store):
        col = make_collection(name="My Collection")
        result = store.create_collection(col)
        assert result is col
        assert store.get_collection(col.id) is col

    def test_create_collection_overwrites_existing_id(self, store):
        original = make_collection(name="Original")
        store.create_collection(original)
        replacement = Collection(id=original.id, name="Replacement")
        store.create_collection(replacement)
        assert store.get_collection(original.id).name == "Replacement"

    def test_get_collection_returns_none_when_missing(self, store):
        assert store.get_collection("nonexistent-id") is None

    def test_get_all_collections_empty(self, store):
        assert store.get_all_collections() == []

    def test_get_all_collections_returns_all(self, store):
        c1 = make_collection(name="A")
        c2 = make_collection(name="B")
        store.create_collection(c1)
        store.create_collection(c2)
        all_cols = store.get_all_collections()
        assert len(all_cols) == 2
        assert c1 in all_cols
        assert c2 in all_cols

    def test_delete_collection_existing(self, store):
        col = make_collection()
        store.create_collection(col)
        assert store.delete_collection(col.id) is True
        assert store.get_collection(col.id) is None

    def test_delete_collection_missing_returns_false(self, store):
        assert store.delete_collection("nonexistent-id") is False

    def test_delete_collection_does_not_delete_prompts(self, store):
        """Deleting a collection leaves its prompts intact (they are not removed)."""
        col = make_collection(name="Dev")
        store.create_collection(col)
        prompt = make_prompt(title="P", collection_id=col.id)
        store.create_prompt(prompt)

        store.delete_collection(col.id)

        # Collection is gone, but the prompt still exists
        assert store.get_collection(col.id) is None
        assert store.get_prompt(prompt.id) is not None
        # Note: storage does NOT unassign collection_id — that is the API layer's job
        assert store.get_prompt(prompt.id).collection_id == col.id


# ============================================================
# get_prompts_by_collection
# ============================================================

class TestGetPromptsByCollection:
    """Tests for retrieving prompts belonging to a collection."""

    def test_returns_matching_prompts(self, store):
        col = make_collection(name="Dev")
        store.create_collection(col)
        p1 = make_prompt(title="A", collection_id=col.id)
        p2 = make_prompt(title="B", collection_id=col.id)
        p3 = make_prompt(title="C", collection_id=None)
        store.create_prompt(p1)
        store.create_prompt(p2)
        store.create_prompt(p3)

        result = store.get_prompts_by_collection(col.id)
        assert len(result) == 2
        assert p1 in result
        assert p2 in result
        assert p3 not in result

    def test_returns_empty_when_no_matches(self, store):
        col = make_collection(name="Empty")
        store.create_collection(col)
        # No prompts assigned
        assert store.get_prompts_by_collection(col.id) == []

    def test_returns_empty_for_nonexistent_collection(self, store):
        assert store.get_prompts_by_collection("nonexistent-id") == []


# ============================================================
# Version Operations
# ============================================================

class TestVersionOperations:
    """Tests for save_version, get_versions, and get_version."""

    def test_save_version_creates_history(self, store):
        prompt = make_prompt()
        store.create_prompt(prompt)
        v1 = make_version(1, title="First")
        store.save_version(prompt.id, v1)
        versions = store.get_versions(prompt.id)
        assert len(versions) == 1
        assert versions[0] is v1

    def test_save_multiple_versions_in_order(self, store):
        prompt = make_prompt()
        store.create_prompt(prompt)
        v1 = make_version(1, title="First")
        v2 = make_version(2, title="Second")
        v3 = make_version(3, title="Third")
        store.save_version(prompt.id, v1)
        store.save_version(prompt.id, v2)
        store.save_version(prompt.id, v3)

        versions = store.get_versions(prompt.id)
        assert len(versions) == 3
        # Versions should be in insertion order
        assert versions[0].title == "First"
        assert versions[1].title == "Second"
        assert versions[2].title == "Third"

    def test_get_versions_empty_when_none_saved(self, store):
        prompt = make_prompt()
        store.create_prompt(prompt)
        assert store.get_versions(prompt.id) == []

    def test_get_versions_empty_for_nonexistent_prompt(self, store):
        assert store.get_versions("nonexistent-id") == []

    def test_get_version_by_number(self, store):
        prompt = make_prompt()
        store.create_prompt(prompt)
        v1 = make_version(1, title="First")
        v2 = make_version(2, title="Second")
        store.save_version(prompt.id, v1)
        store.save_version(prompt.id, v2)

        assert store.get_version(prompt.id, 1) is v1
        assert store.get_version(prompt.id, 2) is v2

    def test_get_version_missing_number_returns_none(self, store):
        prompt = make_prompt()
        store.create_prompt(prompt)
        store.save_version(prompt.id, make_version(1))
        assert store.get_version(prompt.id, 99) is None

    def test_get_version_nonexistent_prompt_returns_none(self, store):
        assert store.get_version("nonexistent-id", 1) is None


# ============================================================
# clear()
# ============================================================

class TestClear:
    """Tests that clear() removes all stored data."""

    def test_clear_removes_all_prompts(self, store):
        p1 = make_prompt(title="A")
        p2 = make_prompt(title="B")
        store.create_prompt(p1)
        store.create_prompt(p2)
        store.clear()
        assert store.get_all_prompts() == []

    def test_clear_removes_all_collections(self, store):
        c1 = make_collection(name="A")
        c2 = make_collection(name="B")
        store.create_collection(c1)
        store.create_collection(c2)
        store.clear()
        assert store.get_all_collections() == []

    def test_clear_removes_all_versions(self, store):
        prompt = make_prompt()
        store.create_prompt(prompt)
        store.save_version(prompt.id, make_version(1))
        store.save_version(prompt.id, make_version(2))
        store.clear()
        assert store.get_versions(prompt.id) == []

    def test_clear_on_empty_storage(self, store):
        """clear() on an already-empty store should not raise."""
        store.clear()
        assert store.get_all_prompts() == []
        assert store.get_all_collections() == []

    def test_clear_removes_everything_at_once(self, store):
        prompt = make_prompt(title="P")
        col = make_collection(name="C")
        store.create_prompt(prompt)
        store.create_collection(col)
        store.save_version(prompt.id, make_version(1))

        store.clear()

        assert store.get_all_prompts() == []
        assert store.get_all_collections() == []
        assert store.get_versions(prompt.id) == []


# ============================================================
# Consistency after create / update / delete cycles
# ============================================================

class TestConsistency:
    """Tests that storage remains consistent after mixed operations."""

    def test_counts_stay_consistent(self, store):
        """Total prompts equals number created minus number deleted."""
        p1 = make_prompt(title="A")
        p2 = make_prompt(title="B")
        p3 = make_prompt(title="C")
        store.create_prompt(p1)
        store.create_prompt(p2)
        store.create_prompt(p3)
        assert len(store.get_all_prompts()) == 3

        store.delete_prompt(p2.id)
        assert len(store.get_all_prompts()) == 2

        store.delete_prompt(p1.id)
        store.delete_prompt(p3.id)
        assert len(store.get_all_prompts()) == 0

    def test_update_does_not_change_count(self, store):
        p1 = make_prompt(title="A")
        store.create_prompt(p1)
        assert len(store.get_all_prompts()) == 1

        updated = Prompt(id=p1.id, title="Updated", content="New")
        store.update_prompt(p1.id, updated)
        assert len(store.get_all_prompts()) == 1

    def test_delete_idempotent(self, store):
        """Deleting the same id twice returns True then False."""
        prompt = make_prompt()
        store.create_prompt(prompt)
        assert store.delete_prompt(prompt.id) is True
        assert store.delete_prompt(prompt.id) is False

    def test_versions_survive_prompt_update(self, store):
        """Updating a prompt does not wipe its version history."""
        prompt = make_prompt(title="Original")
        store.create_prompt(prompt)
        store.save_version(prompt.id, make_version(1, title="Original"))

        updated = Prompt(id=prompt.id, title="Updated", content="New")
        store.update_prompt(prompt.id, updated)

        # Version history should still be intact
        versions = store.get_versions(prompt.id)
        assert len(versions) == 1
        assert versions[0].title == "Original"
        # Current prompt should be the updated one
        assert store.get_prompt(prompt.id).title == "Updated"

    def test_full_lifecycle_consistency(self, store):
        """Create → update → add versions → delete → verify clean state."""
        # 1. Create a collection and a prompt in it
        col = make_collection(name="Dev")
        store.create_collection(col)
        prompt = make_prompt(title="V1", collection_id=col.id)
        store.create_prompt(prompt)
        assert len(store.get_prompts_by_collection(col.id)) == 1

        # 2. Save a version and update the prompt
        store.save_version(prompt.id, make_version(1, title="V1"))
        updated = Prompt(id=prompt.id, title="V2", content="New", collection_id=col.id)
        store.update_prompt(prompt.id, updated)
        assert store.get_prompt(prompt.id).title == "V2"
        assert len(store.get_versions(prompt.id)) == 1

        # 3. Save another version and update again
        store.save_version(prompt.id, make_version(2, title="V2"))
        updated2 = Prompt(id=prompt.id, title="V3", content="Newer", collection_id=col.id)
        store.update_prompt(prompt.id, updated2)
        assert store.get_prompt(prompt.id).title == "V3"
        assert len(store.get_versions(prompt.id)) == 2

        # 4. Delete the prompt — versions must go too
        store.delete_prompt(prompt.id)
        assert store.get_prompt(prompt.id) is None
        assert store.get_versions(prompt.id) == []
        assert len(store.get_prompts_by_collection(col.id)) == 0

        # 5. Collection should still exist
        assert store.get_collection(col.id) is not None

        # 6. Delete the collection
        assert store.delete_collection(col.id) is True
        assert store.get_collection(col.id) is None

        # 7. Storage should be completely empty
        assert store.get_all_prompts() == []
        assert store.get_all_collections() == []
