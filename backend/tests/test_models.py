"""Unit tests for the Pydantic models in app/models.py.

Covers every model: valid creation, required fields, validation errors,
field length limits, defaults/optional fields, generated IDs/timestamps,
and model_dump() serialization.
"""

import pytest
from pydantic import ValidationError

from app.models import (
    Prompt,
    PromptBase,
    PromptCreate,
    PromptUpdate,
    PromptPatch,
    PromptVersion,
    PromptList,
    PromptTestRequest,
    PromptTestResponse,
    VersionList,
    Collection,
    CollectionBase,
    CollectionCreate,
    CollectionList,
    HealthResponse,
)


# ============================================================
# PromptBase
# ============================================================

class TestPromptBase:
    """Tests for the shared base prompt model."""

    def test_valid_creation(self):
        prompt = PromptBase(title="Hello", content="Some content")
        assert prompt.title == "Hello"
        assert prompt.content == "Some content"

    def test_missing_title_raises(self):
        with pytest.raises(ValidationError):
            PromptBase(content="Some content")

    def test_missing_content_raises(self):
        with pytest.raises(ValidationError):
            PromptBase(title="Hello")

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            PromptBase(title="", content="Some content")

    def test_empty_content_raises(self):
        with pytest.raises(ValidationError):
            PromptBase(title="Hello", content="")

    def test_title_max_length(self):
        PromptBase(title="x" * 200, content="content")
        with pytest.raises(ValidationError):
            PromptBase(title="x" * 201, content="content")

    def test_description_max_length(self):
        PromptBase(title="T", content="C", description="d" * 500)
        with pytest.raises(ValidationError):
            PromptBase(title="T", content="C", description="d" * 501)

    def test_optional_fields_defaults(self):
        prompt = PromptBase(title="T", content="C")
        assert prompt.description is None
        assert prompt.collection_id is None
        assert prompt.tags == []

    def test_tags_custom_list(self):
        prompt = PromptBase(title="T", content="C", tags=["a", "b"])
        assert prompt.tags == ["a", "b"]

    def test_description_optional_string(self):
        prompt = PromptBase(title="T", content="C", description="A summary")
        assert prompt.description == "A summary"

    def test_collection_id_optional_string(self):
        prompt = PromptBase(title="T", content="C", collection_id="col-1")
        assert prompt.collection_id == "col-1"


# ============================================================
# PromptCreate
# ============================================================

class TestPromptCreate:
    """Tests for the create-prompt model."""

    def test_valid_creation(self):
        prompt = PromptCreate(title="Hello", content="Some content")
        assert prompt.title == "Hello"
        assert prompt.content == "Some content"

    def test_inherits_validation(self):
        with pytest.raises(ValidationError):
            PromptCreate(title="", content="Some content")
        with pytest.raises(ValidationError):
            PromptCreate(title="Hello", content="")

    def test_defaults_inherited(self):
        prompt = PromptCreate(title="T", content="C")
        assert prompt.description is None
        assert prompt.collection_id is None
        assert prompt.tags == []


# ============================================================
# PromptUpdate
# ============================================================

class TestPromptUpdate:
    """Tests for the full-update (PUT) prompt model."""

    def test_valid_creation(self):
        prompt = PromptUpdate(
            title="New Title",
            content="New content",
            description="desc",
            collection_id="col-1",
            tags=["a"],
        )
        assert prompt.title == "New Title"
        assert prompt.tags == ["a"]

    def test_inherits_validation(self):
        with pytest.raises(ValidationError):
            PromptUpdate(title="x" * 201, content="C")
        with pytest.raises(ValidationError):
            PromptUpdate(title="T", content="")

    def test_defaults_inherited(self):
        prompt = PromptUpdate(title="T", content="C")
        assert prompt.description is None
        assert prompt.collection_id is None
        assert prompt.tags == []


# ============================================================
# PromptPatch
# ============================================================

class TestPromptPatch:
    """Tests for the partial-update (PATCH) prompt model."""

    def test_all_fields_optional(self):
        patch = PromptPatch()
        assert patch.title is None
        assert patch.content is None
        assert patch.description is None
        assert patch.collection_id is None
        assert patch.tags is None

    def test_partial_fields(self):
        patch = PromptPatch(title="New", tags=["x"])
        assert patch.title == "New"
        assert patch.tags == ["x"]
        assert patch.content is None

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            PromptPatch(title="")

    def test_title_max_length(self):
        PromptPatch(title="x" * 200)
        with pytest.raises(ValidationError):
            PromptPatch(title="x" * 201)

    def test_empty_content_raises(self):
        with pytest.raises(ValidationError):
            PromptPatch(content="")

    def test_description_max_length(self):
        PromptPatch(description="d" * 500)
        with pytest.raises(ValidationError):
            PromptPatch(description="d" * 501)


# ============================================================
# Prompt
# ============================================================

class TestPrompt:
    """Tests for the full stored-prompt model."""

    def test_valid_creation(self):
        prompt = Prompt(title="T", content="C")
        assert prompt.title == "T"
        assert prompt.content == "C"

    def test_generated_id(self):
        prompt = Prompt(title="T", content="C")
        assert isinstance(prompt.id, str)
        assert len(prompt.id) > 0

    def test_unique_ids(self):
        p1 = Prompt(title="T", content="C")
        p2 = Prompt(title="T", content="C")
        assert p1.id != p2.id

    def test_generated_timestamps(self):
        prompt = Prompt(title="T", content="C")
        assert prompt.created_at is not None
        assert prompt.updated_at is not None

    def test_explicit_id_overrides_default(self):
        prompt = Prompt(id="custom-id", title="T", content="C")
        assert prompt.id == "custom-id"

    def test_inherits_base_validation(self):
        with pytest.raises(ValidationError):
            Prompt(title="", content="C")
        with pytest.raises(ValidationError):
            Prompt(title="T", content="")

    def test_defaults_inherited(self):
        prompt = Prompt(title="T", content="C")
        assert prompt.description is None
        assert prompt.collection_id is None
        assert prompt.tags == []

    def test_model_dump_keys(self):
        prompt = Prompt(title="T", content="C", tags=["a"])
        dumped = prompt.model_dump()
        assert "id" in dumped
        assert "title" in dumped
        assert "content" in dumped
        assert "description" in dumped
        assert "collection_id" in dumped
        assert "tags" in dumped
        assert "created_at" in dumped
        assert "updated_at" in dumped
        assert dumped["title"] == "T"
        assert dumped["tags"] == ["a"]


# ============================================================
# PromptVersion
# ============================================================

class TestPromptVersion:
    """Tests for the prompt-version snapshot model."""

    def test_valid_creation(self):
        version = PromptVersion(version=1, title="T", content="C")
        assert version.version == 1
        assert version.title == "T"
        assert version.content == "C"

    def test_missing_version_raises(self):
        with pytest.raises(ValidationError):
            PromptVersion(title="T", content="C")

    def test_missing_title_raises(self):
        with pytest.raises(ValidationError):
            PromptVersion(version=1, content="C")

    def test_missing_content_raises(self):
        with pytest.raises(ValidationError):
            PromptVersion(version=1, title="T")

    def test_defaults(self):
        version = PromptVersion(version=1, title="T", content="C")
        assert version.description is None
        assert version.collection_id is None
        assert version.tags == []
        assert version.saved_at is not None

    def test_custom_fields(self):
        version = PromptVersion(
            version=2,
            title="T",
            content="C",
            description="D",
            collection_id="col-1",
            tags=["a", "b"],
        )
        assert version.description == "D"
        assert version.collection_id == "col-1"
        assert version.tags == ["a", "b"]

    def test_model_dump_keys(self):
        version = PromptVersion(version=1, title="T", content="C")
        dumped = version.model_dump()
        assert "version" in dumped
        assert "title" in dumped
        assert "content" in dumped
        assert "description" in dumped
        assert "collection_id" in dumped
        assert "tags" in dumped
        assert "saved_at" in dumped


# ============================================================
# CollectionBase
# ============================================================

class TestCollectionBase:
    """Tests for the shared base collection model."""

    def test_valid_creation(self):
        col = CollectionBase(name="My Collection")
        assert col.name == "My Collection"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            CollectionBase()

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            CollectionBase(name="")

    def test_name_max_length(self):
        CollectionBase(name="x" * 100)
        with pytest.raises(ValidationError):
            CollectionBase(name="x" * 101)

    def test_description_max_length(self):
        CollectionBase(name="N", description="d" * 500)
        with pytest.raises(ValidationError):
            CollectionBase(name="N", description="d" * 501)

    def test_description_default(self):
        col = CollectionBase(name="N")
        assert col.description is None


# ============================================================
# CollectionCreate
# ============================================================

class TestCollectionCreate:
    """Tests for the create-collection model."""

    def test_valid_creation(self):
        col = CollectionCreate(name="My Collection")
        assert col.name == "My Collection"

    def test_inherits_validation(self):
        with pytest.raises(ValidationError):
            CollectionCreate(name="")
        with pytest.raises(ValidationError):
            CollectionCreate(name="x" * 101)

    def test_description_default(self):
        col = CollectionCreate(name="N")
        assert col.description is None


# ============================================================
# Collection
# ============================================================

class TestCollection:
    """Tests for the full stored-collection model."""

    def test_valid_creation(self):
        col = Collection(name="My Collection")
        assert col.name == "My Collection"

    def test_generated_id(self):
        col = Collection(name="N")
        assert isinstance(col.id, str)
        assert len(col.id) > 0

    def test_unique_ids(self):
        c1 = Collection(name="A")
        c2 = Collection(name="B")
        assert c1.id != c2.id

    def test_generated_timestamp(self):
        col = Collection(name="N")
        assert col.created_at is not None

    def test_explicit_id_overrides_default(self):
        col = Collection(id="custom-col-id", name="N")
        assert col.id == "custom-col-id"

    def test_inherits_base_validation(self):
        with pytest.raises(ValidationError):
            Collection(name="")
        with pytest.raises(ValidationError):
            Collection(name="x" * 101)

    def test_model_dump_keys(self):
        col = Collection(name="N", description="D")
        dumped = col.model_dump()
        assert "id" in dumped
        assert "name" in dumped
        assert "description" in dumped
        assert "created_at" in dumped
        assert dumped["name"] == "N"


# ============================================================
# Response / Helper Models
# ============================================================

class TestPromptList:
    """Tests for the PromptList response model."""

    def test_valid_creation(self):
        prompt = Prompt(title="T", content="C")
        pl = PromptList(prompts=[prompt], total=1)
        assert pl.total == 1
        assert len(pl.prompts) == 1

    def test_empty_list(self):
        pl = PromptList(prompts=[], total=0)
        assert pl.total == 0
        assert pl.prompts == []

    def test_model_dump(self):
        prompt = Prompt(title="T", content="C")
        pl = PromptList(prompts=[prompt], total=1)
        dumped = pl.model_dump()
        assert dumped["total"] == 1
        assert isinstance(dumped["prompts"], list)
        assert dumped["prompts"][0]["title"] == "T"


class TestPromptTestRequest:
    """Tests for the PromptTestRequest model."""

    def test_default_empty_variables(self):
        req = PromptTestRequest()
        assert req.variables == {}

    def test_custom_variables(self):
        req = PromptTestRequest(variables={"name": "Ada", "tone": "friendly"})
        assert req.variables["name"] == "Ada"
        assert req.variables["tone"] == "friendly"

    def test_model_dump(self):
        req = PromptTestRequest(variables={"x": "1"})
        dumped = req.model_dump()
        assert dumped == {"variables": {"x": "1"}}


class TestPromptTestResponse:
    """Tests for the PromptTestResponse model."""

    def test_valid_creation(self):
        resp = PromptTestResponse(prompt_id="abc-123", rendered_content="Hello!")
        assert resp.prompt_id == "abc-123"
        assert resp.rendered_content == "Hello!"

    def test_missing_fields_raise(self):
        with pytest.raises(ValidationError):
            PromptTestResponse(prompt_id="abc-123")
        with pytest.raises(ValidationError):
            PromptTestResponse(rendered_content="Hello!")

    def test_model_dump(self):
        resp = PromptTestResponse(prompt_id="abc", rendered_content="Hi")
        dumped = resp.model_dump()
        assert dumped == {"prompt_id": "abc", "rendered_content": "Hi"}


class TestVersionList:
    """Tests for the VersionList response model."""

    def test_valid_creation(self):
        v1 = PromptVersion(version=1, title="T", content="C")
        vl = VersionList(versions=[v1], total=1)
        assert vl.total == 1
        assert len(vl.versions) == 1

    def test_empty_list(self):
        vl = VersionList(versions=[], total=0)
        assert vl.total == 0
        assert vl.versions == []

    def test_model_dump(self):
        v1 = PromptVersion(version=1, title="T", content="C")
        vl = VersionList(versions=[v1], total=1)
        dumped = vl.model_dump()
        assert dumped["total"] == 1
        assert dumped["versions"][0]["version"] == 1


class TestCollectionList:
    """Tests for the CollectionList response model."""

    def test_valid_creation(self):
        col = Collection(name="N")
        cl = CollectionList(collections=[col], total=1)
        assert cl.total == 1
        assert len(cl.collections) == 1

    def test_empty_list(self):
        cl = CollectionList(collections=[], total=0)
        assert cl.total == 0
        assert cl.collections == []

    def test_model_dump(self):
        col = Collection(name="N")
        cl = CollectionList(collections=[col], total=1)
        dumped = cl.model_dump()
        assert dumped["total"] == 1
        assert isinstance(dumped["collections"], list)


class TestHealthResponse:
    """Tests for the HealthResponse model."""

    def test_valid_creation(self):
        resp = HealthResponse(status="healthy", version="0.1.0")
        assert resp.status == "healthy"
        assert resp.version == "0.1.0"

    def test_missing_status_raises(self):
        with pytest.raises(ValidationError):
            HealthResponse(version="0.1.0")

    def test_missing_version_raises(self):
        with pytest.raises(ValidationError):
            HealthResponse(status="healthy")

    def test_model_dump(self):
        resp = HealthResponse(status="healthy", version="0.1.0")
        dumped = resp.model_dump()
        assert dumped == {"status": "healthy", "version": "0.1.0"}
