"""FastAPI routes for PromptLab"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import (
    Prompt, PromptCreate, PromptUpdate,PromptPatch, PromptVersion,
    Collection, CollectionCreate,
    PromptList, CollectionList, HealthResponse,
    PromptTestRequest, PromptTestResponse, VersionList,
    get_current_time
)
from app.storage import storage
from app.utils import sort_prompts_by_date, filter_prompts_by_collection, search_prompts, filter_prompts_by_tag, extract_variables, render_prompt
from app import __version__


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check the health status of the API.

    Returns a simple status payload confirming the service is running,
    along with the currently deployed API version. Useful for load
    balancer health probes and monitoring.

    Returns:
        HealthResponse: An object with ``status`` set to ``"healthy"``
            and ``version`` set to the application's ``__version__``.
    """
    return HealthResponse(status="healthy", version=__version__)


# ============== Prompt Endpoints ==============

@app.get("/prompts", response_model=PromptList)
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None
):
    """List all prompts, with optional filtering and searching.

    Retrieves every stored prompt, then optionally narrows the results
    by collection, search query, and/or tag. When several parameters
    are provided, the filters are applied cumulatively. Results are
    sorted by date with the most recently updated prompts first.

    Args:
        collection_id (Optional[str]): If provided, only prompts
            belonging to the collection with this ID are returned.
        search (Optional[str]): If provided, only prompts matching this
            search query are returned.
        tag (Optional[str]): If provided, only prompts carrying this
            tag are returned.

    Returns:
        PromptList: An object containing the matching ``Prompt``
            objects (newest first) and ``total``, the number of
            matching prompts.
    """
    prompts = storage.get_all_prompts()
    
    # Filter by collection if specified
    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)
    
    # Search if query provided
    if search:
        prompts = search_prompts(prompts, search)

     # Filter by tag if specified
    if tag:
        prompts = filter_prompts_by_tag(prompts, tag)    
    
    # Sort by date (newest first)
    prompts = sort_prompts_by_date(prompts, descending=True)
    
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Retrieve a single prompt by its ID.

    Args:
        prompt_id (str): The unique identifier of the prompt to
            retrieve.

    Returns:
        Prompt: The prompt with the given ID, including its
            server-generated metadata (``id``, ``created_at``,
            ``updated_at``).

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    """Create a new prompt.

    Validates the request body and, if a ``collection_id`` is given,
    checks that the referenced collection exists. The server assigns
    the prompt's ``id``, ``created_at``, and ``updated_at`` fields
    automatically. Responds with status code 201 on success.

    Args:
        prompt_data (PromptCreate): The data for the new prompt:
            ``title``, ``content``, and optionally ``description``,
            ``collection_id``, and ``tags``.

    Returns:
        Prompt: The newly created prompt, including its
            server-generated metadata.

    Raises:
        HTTPException: 400 if ``collection_id`` is provided but no
            collection exists with that ID.
    """
    # Validate collection exists if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Fully replace an existing prompt (PUT semantics).

    Replaces all editable fields of the prompt with the values from
    the request body. Before overwriting, the prompt's current state
    is saved as a new ``PromptVersion`` in its version history. The
    ``id`` and ``created_at`` values are preserved, while
    ``updated_at`` is refreshed.

    Args:
        prompt_id (str): The unique identifier of the prompt to update.
        prompt_data (PromptUpdate): The new values for the prompt:
            ``title``, ``content``, and optionally ``description``,
            ``collection_id``, and ``tags``.

    Returns:
        Prompt: The updated prompt with a refreshed ``updated_at``
            timestamp.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
        HTTPException: 400 if ``collection_id`` is provided but no
            collection exists with that ID.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Validate collection if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

    old_version = PromptVersion(
        version=len(storage.get_versions(prompt_id)) + 1,
        title=existing.title,
        content=existing.content,
        description=existing.description,
        collection_id=existing.collection_id,
        tags=existing.tags,
    )
    storage.save_version(prompt_id, old_version)

    # Build the updated prompt with a fresh updated_at timestamp
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        tags=prompt_data.tags,
        created_at=existing.created_at,
        updated_at=get_current_time()
    )
    
    return storage.update_prompt(prompt_id, updated_prompt)


# Partial update: only the fields sent by the client are changed
@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def patch_prompt(prompt_id: str, prompt_data: PromptPatch):
    """Partially update an existing prompt (PATCH semantics).

    Applies only the fields explicitly provided in the request body;
    omitted fields keep their current values. Before overwriting, the
    prompt's current state is saved as a new ``PromptVersion`` in its
    version history. The ``id`` and ``created_at`` values are
    preserved, while ``updated_at`` is refreshed.

    Args:
        prompt_id (str): The unique identifier of the prompt to update.
        prompt_data (PromptPatch): The fields to change. Any subset of
            ``title``, ``content``, ``description``, ``collection_id``,
            and ``tags`` may be provided.

    Returns:
        Prompt: The updated prompt with the merged field values and a
            refreshed ``updated_at`` timestamp.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
        HTTPException: 400 if a non-null ``collection_id`` is provided
            but no collection exists with that ID.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Keep only the fields the client actually sent
    update_data = prompt_data.model_dump(exclude_unset=True)
    
    # If collection_id is being changed, make sure the collection exists
    if "collection_id" in update_data and update_data["collection_id"] is not None:
        collection = storage.get_collection(update_data["collection_id"])
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

    # Save the current state as a version before overwriting
    old_version = PromptVersion(
        version=len(storage.get_versions(prompt_id)) + 1,
        title=existing.title,
        content=existing.content,
        description=existing.description,
        collection_id=existing.collection_id,
        tags=existing.tags,
    )
    storage.save_version(prompt_id, old_version)
    # Build the updated prompt: new values where provided, old values otherwise
    updated_prompt = Prompt(
        id=existing.id,
        title=update_data.get("title", existing.title),
        content=update_data.get("content", existing.content),
        description=update_data.get("description", existing.description),
        collection_id=update_data.get("collection_id", existing.collection_id),
        tags=update_data.get("tags", existing.tags),
        created_at=existing.created_at,
        updated_at=get_current_time()
    )
    
    return storage.update_prompt(prompt_id, updated_prompt)


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    """Delete a prompt by its ID.

    Permanently removes the prompt from storage. Responds with status
    code 204 and an empty body on success.

    Args:
        prompt_id (str): The unique identifier of the prompt to delete.

    Returns:
        None: Always returns None; the response has status code 204
            with no content.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
    """
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None

@app.post("/prompts/{prompt_id}/test", response_model=PromptTestResponse)
def test_prompt(prompt_id: str, test_data: PromptTestRequest):
    """Render a prompt template with test variable values.

    Extracts every ``{{variable}}`` placeholder from the prompt's
    content and verifies that the request supplies a value for each
    one. If all required values are present, the template is rendered
    by substituting the provided values, letting users preview the
    exact text that would be sent to an LLM.

    Args:
        prompt_id (str): The unique identifier of the prompt to test.
        test_data (PromptTestRequest): A mapping of template variable
            names (without the ``{{ }}`` delimiters) to the string
            values to substitute into the prompt content.

    Returns:
        PromptTestResponse: An object containing the ``prompt_id`` and
            the ``rendered_content`` with all variables replaced.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
        HTTPException: 400 if values are missing for one or more
            template variables.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Find all {{variables}} the template requires
    required_vars = extract_variables(prompt.content)
    
    # Check the user provided a value for every required variable
    missing = [v for v in required_vars if v not in test_data.variables]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing values for variables: {', '.join(missing)}"
        )
    
    # Render the template with the provided values
    rendered = render_prompt(prompt.content, test_data.variables)
    return PromptTestResponse(prompt_id=prompt.id, rendered_content=rendered)

@app.get("/prompts/{prompt_id}/versions", response_model=VersionList)
def list_versions(prompt_id: str):
    """List the saved version history of a prompt.

    Returns every snapshot captured before the prompt's past updates.

    Args:
        prompt_id (str): The unique identifier of the prompt whose
            version history is requested.

    Returns:
        VersionList: An object containing the saved ``PromptVersion``
            snapshots and ``total``, the number of saved versions.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    versions = storage.get_versions(prompt_id)
    return VersionList(versions=versions, total=len(versions))


@app.get("/prompts/{prompt_id}/versions/{version_number}", response_model=PromptVersion)
def get_prompt_version(prompt_id: str, version_number: int):
    """Retrieve a specific version from a prompt's history.

    Args:
        prompt_id (str): The unique identifier of the prompt whose
            version is requested.
        version_number (int): The sequential version number to
            retrieve, starting at 1 for the first saved snapshot.

    Returns:
        PromptVersion: The snapshot of the prompt's state saved under
            the given version number.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID, or
            if the prompt has no version with the given number.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    version = storage.get_version(prompt_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

# ============== Collection Endpoints ==============

@app.get("/collections", response_model=CollectionList)
def list_collections():
    """List all collections.

    Returns:
        CollectionList: An object containing every stored
            ``Collection`` and ``total``, the number of collections.
    """
    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Retrieve a single collection by its ID.

    Args:
        collection_id (str): The unique identifier of the collection
            to retrieve.

    Returns:
        Collection: The collection with the given ID, including its
            server-generated metadata (``id``, ``created_at``).

    Raises:
        HTTPException: 404 if no collection exists with the given ID.
    """
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    """Create a new collection.

    The server assigns the collection's ``id`` and ``created_at``
    fields automatically. Responds with status code 201 on success.

    Args:
        collection_data (CollectionCreate): The data for the new
            collection: ``name`` and optionally ``description``.

    Returns:
        Collection: The newly created collection, including its
            server-generated metadata.
    """
    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a collection by its ID.

    All prompts belonging to the collection are first unassigned
    (their ``collection_id`` is set to None) rather than deleted; the
    collection itself is then removed. Responds with status code 204
    and an empty body on success.

    Args:
        collection_id (str): The unique identifier of the collection
            to delete.

    Returns:
        None: Always returns None; the response has status code 204
            with no content.

    Raises:
        HTTPException: 404 if no collection exists with the given ID.
    """
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Unassign all prompts that belong to this collection
    prompts_in_collection = storage.get_prompts_by_collection(collection_id)
    for prompt in prompts_in_collection:
        prompt.collection_id = None
    
    # Now it's safe to delete the collection
    storage.delete_collection(collection_id)
    return None

