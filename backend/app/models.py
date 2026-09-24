"""Pydantic models for PromptLab"""

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


def generate_id() -> str:
    """Generate a unique UUID4 identifier.

    Returns:
        str: A UUID4 string.
    """
    return str(uuid4())


def get_current_time() -> datetime:
    """Get the current UTC datetime.

    Returns:
        datetime: The current UTC datetime.
    """
    return datetime.now(timezone.utc)


# ============== Prompt Models ==============

class PromptBase(BaseModel):
    """Base model for a prompt, containing the shared core fields.

    This model defines the common attributes for prompt creation and
    update operations. It is inherited by ``PromptCreate``,
    ``PromptUpdate``, and ``Prompt`` to ensure consistent validation.

    Attributes:
        title (str): The prompt's title. Required, must be between 1 and
            200 characters.
        content (str): The full text of the prompt. May include template
            variables in ``{{variable}}`` format. Required, must not be
            empty.
        description (Optional[str]): A short human-readable summary of the
            prompt's purpose. Optional, up to 500 characters. Defaults to
            None.
        collection_id (Optional[str]): The ID of the collection this prompt
            belongs to, if any. Defaults to None.
        tags (List[str]): A list of tags for categorizing and filtering the
            prompt. Defaults to an empty list.

    Example:
        Creating a prompt with template variables and tags::

            prompt = PromptBase(
                title="Summarize Article",
                content="Summarize the following article: {{article_text}}",
                description="Generates a concise summary of an article.",
                collection_id="col-123",
                tags=["summarization", "nlp"]
            )
    """
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: str | None = Field(None, max_length=500)
    collection_id: str | None = None
    tags: list[str] = Field(default_factory=list)


class PromptCreate(PromptBase):
    """Model for creating a new prompt.

    Inherits all fields from ``PromptBase``. All inherited fields are
    validated on creation; the server assigns ``id``, ``created_at``,
    and ``updated_at`` automatically.

    Attributes:
        title (str): The prompt's title. Required, must be between 1 and
            200 characters.
        content (str): The full text of the prompt. May include template
            variables in ``{{variable}}`` format. Required, must not be
            empty.
        description (Optional[str]): A short human-readable summary of the
            prompt's purpose. Optional, up to 500 characters. Defaults to
            None.
        collection_id (Optional[str]): The ID of the collection this prompt
            belongs to, if any. Defaults to None.
        tags (List[str]): A list of tags for categorizing and filtering the
            prompt. Defaults to an empty list.

    Example:
        Creating a new prompt via the API request body::

            new_prompt = PromptCreate(
                title="Code Review",
                content="Review the following code: {{code}}",
                description="Generates a code review with suggestions.",
                tags=["code", "review"]
            )
    """


class PromptUpdate(PromptBase):
    """Model for fully replacing an existing prompt (PUT semantics).

    Inherits all fields from ``PromptBase``. Every field must be provided
    for a full update, since any omitted field falls back to its default
    value. For partial updates where only some fields change, use
    ``PromptPatch`` instead. The ``id`` and ``created_at`` values are
    preserved; ``updated_at`` is refreshed by the server.

    Attributes:
        title (str): The prompt's title. Required, must be between 1 and
            200 characters.
        content (str): The full text of the prompt. May include template
            variables in ``{{variable}}`` format. Required, must not be
            empty.
        description (Optional[str]): A short human-readable summary of the
            prompt's purpose. Optional, up to 500 characters. Defaults to
            None.
        collection_id (Optional[str]): The ID of the collection this prompt
            belongs to, if any. Defaults to None.
        tags (List[str]): A list of tags for categorizing and filtering the
            prompt. Defaults to an empty list.

    Example:
        Replacing an existing prompt via the API request body::

            updated_prompt = PromptUpdate(
                title="Code Review v2",
                content="Review the following code in detail: {{code}}",
                description="Generates a thorough code review.",
                collection_id="col-456",
                tags=["code", "review", "v2"]
            )
    """


class PromptPatch(BaseModel):
    """Model for partially updating an existing prompt (PATCH semantics).

    All fields are optional: only the fields explicitly provided in the
    request are updated, while omitted fields retain their current values.
    For a full replacement where every field is required, use
    ``PromptUpdate`` instead. The ``id`` and ``created_at`` values are
    preserved; ``updated_at`` is refreshed by the server.

    Attributes:
        title (Optional[str]): The prompt's new title. If provided, must
            be between 1 and 200 characters. Defaults to None.
        content (Optional[str]): The new full text of the prompt. May
            include template variables in ``{{variable}}`` format. If
            provided, must not be empty. Defaults to None.
        description (Optional[str]): A new short human-readable summary of
            the prompt's purpose, up to 500 characters. Defaults to None.
        collection_id (Optional[str]): The ID of the collection to move the
            prompt to, if any. Defaults to None.
        tags (Optional[List[str]]): A new list of tags for categorizing and
            filtering the prompt, replacing the existing tags. Defaults to
            None.

    Example:
        Updating only the title and tags of an existing prompt::

            patch = PromptPatch(
                title="Code Review v3",
                tags=["code", "review", "v3"]
            )
    """
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)
    description: str | None = Field(None, max_length=500)
    collection_id: str | None = None
    tags: list[str] | None = None


class Prompt(PromptBase):
    """Complete prompt model as stored and returned by the API.

    Inherits all fields from ``PromptBase`` and adds server-generated
    metadata. This model is used in API responses and internal storage;
    use ``PromptCreate``, ``PromptUpdate``, or ``PromptPatch`` for
    request bodies.

    Attributes:
        title (str): The prompt's title. Required, must be between 1 and
            200 characters.
        content (str): The full text of the prompt. May include template
            variables in ``{{variable}}`` format. Required, must not be
            empty.
        description (Optional[str]): A short human-readable summary of the
            prompt's purpose. Optional, up to 500 characters. Defaults to
            None.
        collection_id (Optional[str]): The ID of the collection this prompt
            belongs to, if any. Defaults to None.
        tags (List[str]): A list of tags for categorizing and filtering the
            prompt. Defaults to an empty list.
        id (str): The unique identifier of the prompt. Auto-generated as a
            UUID4 string on creation.
        created_at (datetime): The UTC timestamp of when the prompt was
            created. Auto-generated on creation.
        updated_at (datetime): The UTC timestamp of when the prompt was
            last updated. Auto-generated on creation and refreshed on each
            update.

    Example:
        Accessing server-generated fields on a stored prompt::

            prompt = Prompt(
                title="Summarize Article",
                content="Summarize the following article: {{article_text}}",
                description="Generates a concise summary of an article.",
                tags=["summarization", "nlp"]
            )
            print(prompt.id)          # auto-generated UUID4
            print(prompt.created_at)  # auto-set creation timestamp
    """
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

    class Config:
         """Configure attribute-based model creation for Prompt."""
         from_attributes = True

class PromptVersion(BaseModel):
    """A snapshot of a prompt's state before an update.

    Whenever a prompt is modified, the API captures its previous state as
    a ``PromptVersion`` and stores it in a per-prompt history. Versions
    allow users to inspect or restore earlier content. Unlike ``Prompt``,
    this model contains no ``id``, ``created_at``, or ``updated_at``
    fields, since a version is an immutable historical record rather than
    a live entity.

    Attributes:
        version (int): The sequential version number of the snapshot,
            starting at 1 for the first saved state and incrementing by
            one with each subsequent update of the prompt.
        title (str): The prompt's title at the time the snapshot was
            taken.
        content (str): The full text of the prompt at the time the
            snapshot was taken, including any ``{{variable}}`` template
            placeholders.
        description (Optional[str]): The prompt's description at the time
            the snapshot was taken. Defaults to None.
        collection_id (Optional[str]): The ID of the collection the prompt
            belonged to at the time the snapshot was taken. Defaults to
            None.
        tags (List[str]): The tags assigned to the prompt at the time the
            snapshot was taken. Defaults to an empty list.
        saved_at (datetime): The UTC timestamp of when the snapshot was
            saved. Auto-generated on creation.

    Example:
        Capturing a prompt's state before overwriting it::

            old_version = PromptVersion(
                version=len(storage.get_versions(prompt_id)) + 1,
                title=existing.title,
                content=existing.content,
                description=existing.description,
                collection_id=existing.collection_id,
                tags=existing.tags
            )
            storage.save_version(prompt_id, old_version)
    """
    version: int
    title: str
    content: str
    description: str | None = None
    collection_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    saved_at: datetime = Field(default_factory=get_current_time)        


# ============== Collection Models ==============

class CollectionBase(BaseModel):
    """Base model for a collection, containing the shared core fields.

    This model defines the common attributes for collection creation
    operations. It is inherited by ``CollectionCreate`` and
    ``Collection`` to ensure consistent validation. Collections are used
    to group related prompts together for organization and filtering.

    Attributes:
        name (str): The collection's name. Required, must be between 1
            and 100 characters.
        description (Optional[str]): A short human-readable summary of
            the collection's purpose. Optional, up to 500 characters.
            Defaults to None.

    Example:
        Creating a collection to group related prompts::

            collection = CollectionBase(
                name="Summarization Prompts",
                description="Prompts for summarizing articles and documents."
            )
    """
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class CollectionCreate(CollectionBase):
    """Model for creating a new collection.

    Inherits all fields from ``CollectionBase``. All inherited fields are
    validated on creation; the server assigns ``id`` and ``created_at``
    automatically.

    Attributes:
        name (str): The collection's name. Required, must be between 1
            and 100 characters.
        description (Optional[str]): A short human-readable summary of
            the collection's purpose. Optional, up to 500 characters.
            Defaults to None.

    Example:
        Creating a new collection via the API request body::

            new_collection = CollectionCreate(
                name="Code Review Prompts",
                description="Prompts for reviewing and improving code."
            )
    """


class Collection(CollectionBase):
    """Complete collection model as stored and returned by the API.

    Inherits all fields from ``CollectionBase`` and adds server-generated
    metadata. This model is used in API responses and internal storage;
    use ``CollectionCreate`` for request bodies.

    Attributes:
        name (str): The collection's name. Required, must be between 1
            and 100 characters.
        description (Optional[str]): A short human-readable summary of
            the collection's purpose. Optional, up to 500 characters.
            Defaults to None.
        id (str): The unique identifier of the collection. Auto-generated
            as a UUID4 string on creation.
        created_at (datetime): The UTC timestamp of when the collection
            was created. Auto-generated on creation.

    Example:
        Accessing server-generated fields on a stored collection::

            collection = Collection(
                name="Summarization Prompts",
                description="Prompts for summarizing articles and documents."
            )
            print(collection.id)          # auto-generated UUID4
            print(collection.created_at)  # auto-set creation timestamp
    """
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)

    class Config:
        """Configure attribute-based model creation for Collection."""
        from_attributes = True


# ============== Response Models ==============

class PromptList(BaseModel):
    """List of prompts returned by the list prompts endpoint.

    This model wraps a collection of ``Prompt`` objects together with
    the total number of matching prompts, enabling clients to display
    result counts and implement pagination or infinite scrolling.

    Attributes:
        prompts (List[Prompt]): The prompt objects matching the
                        request's filters (e.g. collection, tags, search query),
            sorted by most recently created first.
        total (int): The total number of prompts matching the request's
            filters.

    Example:
        Returning the filtered prompts from the list endpoint::

            prompts = sort_prompts_by_date(prompts, descending=True)
            return PromptList(prompts=prompts, total=len(prompts))
    """
    prompts: list[Prompt]
    total: int

class PromptTestRequest(BaseModel):
    """Values to fill into a prompt template's ``{{variables}}``.

    This model is used as the request body for the prompt test endpoint.
    Each key must match a ``{{variable}}`` placeholder in the prompt's
    content (without the ``{{ }}`` delimiters), and its value is
    substituted into the template during rendering.

    Attributes:
        variables (Dict[str, str]): A mapping of template variable names
            to the string values that should replace them in the prompt
            content. Defaults to an empty dict, which leaves all
            placeholders unreplaced.

    Example:
        Testing a prompt template with sample values::

            test_data = PromptTestRequest(
                variables={
                    "article_text": "The quick brown fox...",
                    "max_words": "100"
                }
            )
            rendered = render_prompt(prompt.content, test_data.variables)
    """
    variables: dict[str, str] = Field(default_factory=dict)


class PromptTestResponse(BaseModel):
    """The prompt content with all variables replaced by values.

    This model is returned by the prompt test endpoint after rendering
    a prompt template with the values supplied in a
    ``PromptTestRequest``. It lets users preview the exact text that
    would be sent to an LLM.

    Attributes:
        prompt_id (str): The unique identifier of the prompt whose
            template was rendered.
        rendered_content (str): The prompt's content with each
            ``{{variable}}`` placeholder replaced by its corresponding
            value from the test request.

    Example:
        Returning the rendered template from the test endpoint::

            rendered = render_prompt(prompt.content, test_data.variables)
            return PromptTestResponse(
                prompt_id=prompt.id,
                rendered_content=rendered
            )
    """
    prompt_id: str
    rendered_content: str

class VersionList(BaseModel):
    """List of saved versions in a prompt's edit history.

    This model wraps a collection of ``PromptVersion`` snapshots
    together with the total count. It is returned by the version
    history endpoint, allowing clients to inspect or restore earlier
    states of a prompt.

    Attributes:
        versions (List[PromptVersion]): The saved snapshot objects
                        representing previous states of the prompt, ordered from
            oldest to newest (insertion order).
        total (int): The total number of versions saved for the prompt.

    Example:
        Returning a prompt's version history from an endpoint::

            versions = storage.get_versions(prompt_id)
            return VersionList(versions=versions, total=len(versions))
    """
    versions: list[PromptVersion]
    total: int


class CollectionList(BaseModel):
    """List of collections returned by the list collections endpoint.

    This model wraps a collection of ``Collection`` objects together
    with the total number of collections, enabling clients to display
    result counts and organize prompts by group.

    Attributes:
        collections (List[Collection]): The collection objects currently
            stored in the system.
        total (int): The total number of collections in the system.

    Example:
        Returning all collections from the list endpoint::

            collections = storage.get_all_collections()
            return CollectionList(
                collections=collections,
                total=len(collections)
            )
    """
    collections: list[Collection]
    total: int


class HealthResponse(BaseModel):
    """Service health status returned by the health check endpoint.

    This model is used by load balancers, monitoring tools, and
    deployment pipelines to verify that the API is running and to
    identify which version is currently deployed.

    Attributes:
        status (str): The current health status of the service, e.g.
            ``"healthy"``.
        version (str): The version string of the running API, taken
            from the application's ``__version__``.

    Example:
        Returning the service status from the health check endpoint::

            @app.get("/health", response_model=HealthResponse)
            def health_check():
                return HealthResponse(status="healthy", version=__version__)
    """
    status: str
    version: str



