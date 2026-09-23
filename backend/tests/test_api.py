"""API tests for PromptLab

These tests verify the API endpoints work correctly.
Students should expand these tests significantly in Week 3.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealth:
    """Tests for health endpoint."""
    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPrompts:
    """Tests for prompt endpoints."""
    def test_create_prompt(self, client: TestClient, sample_prompt_data):
        response = client.post("/prompts", json=sample_prompt_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]
        assert "id" in data
        assert "created_at" in data
    
    def test_list_prompts_empty(self, client: TestClient):
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert data["prompts"] == []
        assert data["total"] == 0
    
    def test_list_prompts_with_data(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        client.post("/prompts", json=sample_prompt_data)
        
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert len(data["prompts"]) == 1
        assert data["total"] == 1
    
    def test_get_prompt_success(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        
        response = client.get(f"/prompts/{prompt_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prompt_id
    
    def test_get_prompt_not_found(self, client: TestClient):
        """Test that getting a non-existent prompt returns 404."""
        response = client.get("/prompts/nonexistent-id")
        # This should be 404, but there's a bug...
        assert response.status_code == 404  # Will fail until bug is fixed
    
    def test_delete_prompt(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/prompts/{prompt_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/prompts/{prompt_id}")
        assert get_response.status_code in [404, 500]  # 404 after fix
    
    def test_update_prompt(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]
        
        # Update it
        updated_data = {
            "title": "Updated Title",
            "content": "Updated content for the prompt",
            "description": "Updated description"
        }
        
        import time
        time.sleep(0.1)  # Small delay to ensure timestamp would change
        
        response = client.put(f"/prompts/{prompt_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        
        # The updated_at should be different from original
        assert data["updated_at"] != original_updated_at  # Uncomment after fix

    def test_patch_prompt_partial(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        
        # Update ONLY the title via PATCH
        response = client.patch(f"/prompts/{prompt_id}", json={"title": "Patched Title"})
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Patched Title"
        # Everything else must be untouched
        assert data["content"] == sample_prompt_data["content"]
        assert data["description"] == sample_prompt_data["description"]
    
    def test_patch_prompt_not_found(self, client: TestClient):
        response = client.patch("/prompts/nonexistent-id", json={"title": "X"})
        assert response.status_code == 404 

    def test_create_prompt_with_tags(self, client: TestClient, sample_prompt_data):
        data = {**sample_prompt_data, "tags": ["coding", "review"]}
        response = client.post("/prompts", json=data)
        assert response.status_code == 201
        assert response.json()["tags"] == ["coding", "review"]
    
    def test_filter_prompts_by_tag(self, client: TestClient):
        client.post("/prompts", json={"title": "A", "content": "Content A here", "tags": ["coding"]})
        client.post("/prompts", json={"title": "B", "content": "Content B here", "tags": ["writing"]})
        
        response = client.get("/prompts?tag=coding")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["title"] == "A"

    def test_test_prompt_success(self, client: TestClient, sample_prompt_data):
        # sample_prompt_data content contains {{code}}
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]
        
        response = client.post(
            f"/prompts/{prompt_id}/test",
            json={"variables": {"code": "print('hello')"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prompt_id"] == prompt_id
        assert "print('hello')" in data["rendered_content"]
        assert "{{code}}" not in data["rendered_content"]
    
    def test_test_prompt_missing_variable(self, client: TestClient, sample_prompt_data):
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]
        
        response = client.post(f"/prompts/{prompt_id}/test", json={"variables": {}})
        assert response.status_code == 400
    
    def test_test_prompt_not_found(self, client: TestClient):
        response = client.post("/prompts/bad-id/test", json={"variables": {}})
        assert response.status_code == 404     

    def test_sorting_order(self, client: TestClient):
        """Test that prompts are sorted newest first. """
        import time
        
        # Create prompts with delay
        prompt1 = {"title": "First", "content": "First prompt content"}
        prompt2 = {"title": "Second", "content": "Second prompt content"}
        
        client.post("/prompts", json=prompt1)
        time.sleep(0.1)
        client.post("/prompts", json=prompt2)
        
        response = client.get("/prompts")
        prompts = response.json()["prompts"]
        
        # Newest (Second) should be first
        assert prompts[0]["title"] == "Second"  

    def test_version_history_created_on_update(self, client: TestClient, sample_prompt_data):
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]
        
        # Update the prompt via PUT
        client.put(f"/prompts/{prompt_id}", json={
            "title": "Updated Title",
            "content": "Updated content here"
        })
        
        response = client.get(f"/prompts/{prompt_id}/versions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        # Version 1 should hold the ORIGINAL values
        assert data["versions"][0]["title"] == sample_prompt_data["title"]
    
    def test_get_specific_version(self, client: TestClient, sample_prompt_data):
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]
        
        client.patch(f"/prompts/{prompt_id}", json={"title": "V2 Title"})
        client.patch(f"/prompts/{prompt_id}", json={"title": "V3 Title"})
        
        response = client.get(f"/prompts/{prompt_id}/versions/1")
        assert response.status_code == 200
        assert response.json()["title"] == sample_prompt_data["title"]
        
        response2 = client.get(f"/prompts/{prompt_id}/versions/2")
        assert response2.status_code == 200
        assert response2.json()["title"] == "V2 Title"
    
    def test_versions_not_found(self, client: TestClient):
        response = client.get("/prompts/bad-id/versions")
        assert response.status_code == 404

    # ---- New tests for uncovered branches ----

    def test_filter_prompts_by_collection_id(self, client: TestClient):
        """GET /prompts?collection_id=... narrows results to that collection."""
        # Create a collection
        col = client.post("/collections", json={"name": "Dev"}).json()
        # Create one prompt in the collection and one without
        client.post("/prompts", json={
            "title": "In Collection",
            "content": "Content A",
            "collection_id": col["id"],
        })
        client.post("/prompts", json={"title": "No Collection", "content": "Content B"})

        response = client.get(f"/prompts?collection_id={col['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["title"] == "In Collection"

    def test_filter_prompts_by_search(self, client: TestClient):
        """GET /prompts?search=... matches titles case-insensitively."""
        client.post("/prompts", json={"title": "Code Review", "content": "Content A"})
        client.post("/prompts", json={"title": "Recipe", "content": "Content B"})

        response = client.get("/prompts?search=code")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["title"] == "Code Review"
    
    def test_filter_prompts_combined(self, client: TestClient):
        """collection_id, search, and tag filters combine cumulatively (AND)."""
        col = client.post("/collections", json={"name": "Dev"}).json()
        client.post("/prompts", json={
            "title": "Code Review",
            "content": "Review code",
            "collection_id": col["id"],
            "tags": ["coding"],
        })
        # This one is in the collection but doesn't match the search
        client.post("/prompts", json={
            "title": "Recipe",
            "content": "Cook pasta",
            "collection_id": col["id"],
            "tags": ["cooking"],
        })
        # This one matches the search but is not in the collection
        client.post("/prompts", json={
            "title": "Code Refactor",
            "content": "Refactor code",
            "tags": ["coding"],
        })

        response = client.get(
            f"/prompts?collection_id={col['id']}&search=code&tag=coding"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["title"] == "Code Review"
    
    def test_create_prompt_invalid_collection_id(self, client: TestClient):
        """POST /prompts with a non-existent collection_id returns 400."""
        response = client.post("/prompts", json={
            "title": "Test",
            "content": "Content",
            "collection_id": "nonexistent-col",
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection not found"

    def test_update_prompt_not_found(self, client: TestClient):
        """PUT /prompts/{bad-id} returns 404."""
        response = client.put("/prompts/nonexistent-id", json={
            "title": "Updated",
            "content": "Updated content",
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    def test_update_prompt_invalid_collection_id(self, client: TestClient, sample_prompt_data):
        """PUT /prompts/{id} with a non-existent collection_id returns 400."""
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]
        
        response = client.put(f"/prompts/{prompt_id}", json={
            "title": "Updated",
            "content": "Updated content",
            "collection_id": "nonexistent-col",
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection not found"

    def test_patch_prompt_invalid_collection_id(self, client: TestClient, sample_prompt_data):
        """PATCH /prompts/{id} with a non-existent collection_id returns 400."""
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]
        
        response = client.patch(f"/prompts/{prompt_id}", json={
            "collection_id": "nonexistent-col",
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection not found"

    def test_delete_prompt_not_found(self, client: TestClient):
        """DELETE /prompts/{bad-id} returns 404."""
        response = client.delete("/prompts/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    def test_get_version_prompt_not_found(self, client: TestClient):
        """GET /prompts/{bad-id}/versions/1 returns 404 (prompt not found)."""
        response = client.get("/prompts/nonexistent-id/versions/1")
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    def test_get_version_number_not_found(self, client: TestClient, sample_prompt_data):
        """GET /prompts/{id}/versions/99 returns 404 (version not found)."""
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]

        response = client.get(f"/prompts/{prompt_id}/versions/99")
        assert response.status_code == 404
        assert response.json()["detail"] == "Version not found"


class TestCollections:
    """Tests for collection endpoints."""
    def test_create_collection(self, client: TestClient, sample_collection_data):
        response = client.post("/collections", json=sample_collection_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_collection_data["name"]
        assert "id" in data

    def test_list_collections(self, client: TestClient, sample_collection_data):
        client.post("/collections", json=sample_collection_data)
        
        response = client.get("/collections")
        assert response.status_code == 200
        data = response.json()
        assert len(data["collections"]) == 1

    def test_get_collection_not_found(self, client: TestClient):
        response = client.get("/collections/nonexistent-id")
        assert response.status_code == 404

    def test_delete_collection_with_prompts(self, client: TestClient, sample_collection_data, sample_prompt_data):
        """Test deleting a collection that has prompts. """
        # Create collection
        col_response = client.post("/collections", json=sample_collection_data)
        collection_id = col_response.json()["id"]

        # Create prompt in collection
        prompt_data = {**sample_prompt_data, "collection_id": collection_id}
        prompt_response = client.post("/prompts", json=prompt_data)
        prompt_id = prompt_response.json()["id"]

        # Delete collection
        client.delete(f"/collections/{collection_id}")

       # The prompt still exists but is now unassigned
        prompts = client.get("/prompts").json()["prompts"]
        assert len(prompts) == 1
        assert prompts[0]["collection_id"] is None

    # ---- New tests for uncovered branches ----

    def test_get_collection_success(self, client: TestClient, sample_collection_data):
        """GET /collections/{id} returns 200 with the collection data."""
        create = client.post("/collections", json=sample_collection_data)
        collection_id = create.json()["id"]

        response = client.get(f"/collections/{collection_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == collection_id
        assert data["name"] == sample_collection_data["name"]

    def test_delete_collection_not_found(self, client: TestClient):
        """DELETE /collections/{bad-id} returns 404."""
        response = client.delete("/collections/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Collection not found"


class TestRestore:
    """Tests for POST /prompts/{prompt_id}/versions/{version_number}/restore.

    These tests follow the spec in specs/prompt-versions.md (AC-4.1 through
    AC-4.7 and E-7).  They are expected to FAIL until the restore endpoint
    is implemented in app/api.py.
    """

    # ---- AC-4.1: Restore happy path ----

    def test_restore_happy_path(self, client: TestClient, sample_prompt_data):
        """POST restore returns 200 with the version's field values."""
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]

        # Update the prompt so version 1 captures the original state
        client.put(f"/prompts/{prompt_id}", json={
            "title": "Changed",
            "content": "Changed content",
        })

        # Restore to version 1 (the original)
        response = client.post(f"/prompts/{prompt_id}/versions/1/restore")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]

    # ---- AC-4.2: Restore snapshots current state first ----

    def test_restore_snapshots_current_state(self, client: TestClient, sample_prompt_data):
        """Restore saves the pre-restore state as a new version."""
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]

        # Update -> version 1 holds the original
        client.put(f"/prompts/{prompt_id}", json={
            "title": "Changed",
            "content": "Changed content",
        })
        # Before restore there is 1 version
        assert client.get(f"/prompts/{prompt_id}/versions").json()["total"] == 1

        # Restore to version 1
        client.post(f"/prompts/{prompt_id}/versions/1/restore")

        # Now there should be 2 versions; version 2 holds the "Changed" state
        versions = client.get(f"/prompts/{prompt_id}/versions").json()
        assert versions["total"] == 2
        assert versions["versions"][1]["title"] == "Changed"

    # ---- AC-4.3: Identity fields preserved, updated_at refreshed ----

    def test_restore_preserves_id_and_created_at_refreshes_updated_at(
        self, client: TestClient, sample_prompt_data
    ):
        """Restore keeps id and created_at, but refreshes updated_at."""
        import time

        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]
        original_created_at = create.json()["created_at"]
        original_updated_at = create.json()["updated_at"]

        # Update to create a version, then wait so updated_at can change
        client.put(f"/prompts/{prompt_id}", json={
            "title": "Changed",
            "content": "Changed content",
        })
        time.sleep(0.1)

        response = client.post(f"/prompts/{prompt_id}/versions/1/restore")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == prompt_id
        assert data["created_at"] == original_created_at
        assert data["updated_at"] != original_updated_at

    # ---- AC-4.5: Unknown prompt -> 404 ----

    def test_restore_unknown_prompt(self, client: TestClient):
        """POST restore with an unknown prompt_id returns 404."""
        response = client.post("/prompts/nonexistent-id/versions/1/restore")
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    # ---- AC-4.6: Unknown version -> 404, prompt unchanged ----

    def test_restore_unknown_version(self, client: TestClient, sample_prompt_data):
        """POST restore with an unknown version number returns 404 and leaves the prompt unchanged."""
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]
        original_title = create.json()["title"]

        response = client.post(f"/prompts/{prompt_id}/versions/99/restore")
        assert response.status_code == 404
        assert response.json()["detail"] == "Version not found"

        # Prompt must be unchanged
        prompt = client.get(f"/prompts/{prompt_id}").json()
        assert prompt["title"] == original_title

        # No snapshot should have been created
        versions = client.get(f"/prompts/{prompt_id}/versions").json()
        assert versions["total"] == 0

    # ---- E-7: Restore with deleted collection -> 400, no state change ----

    def test_restore_deleted_collection(self, client: TestClient, sample_prompt_data):
        """Restore a version whose collection_id references a deleted collection returns 400."""
        # Create a collection and a prompt in it
        col = client.post("/collections", json={"name": "Dev"}).json()
        prompt_data = {**sample_prompt_data, "collection_id": col["id"]}
        create = client.post("/prompts", json=prompt_data)
        prompt_id = create.json()["id"]

        # Update the prompt (unassign from collection) - version 1 still has the collection_id
        client.put(f"/prompts/{prompt_id}", json={
            "title": "Changed",
            "content": "Changed content",
            "collection_id": None,
        })

        # Delete the collection so version 1's collection_id is now stale
        client.delete(f"/collections/{col['id']}")

        # Attempt to restore version 1 - should fail with 400
        response = client.post(f"/prompts/{prompt_id}/versions/1/restore")
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection not found"

        # Prompt must be unchanged (still "Changed")
        prompt = client.get(f"/prompts/{prompt_id}").json()
        assert prompt["title"] == "Changed"

        # No new snapshot should have been created (still just the 1 from the PUT)
        versions = client.get(f"/prompts/{prompt_id}/versions").json()
        assert versions["total"] == 1

    # ---- AC-4.7: Restore is repeatable ----

    def test_restore_repeatable(self, client: TestClient, sample_prompt_data):
        """Calling restore twice succeeds both times; each call adds one snapshot."""
        create = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create.json()["id"]

        # Update to create version 1
        client.put(f"/prompts/{prompt_id}", json={
            "title": "Changed",
            "content": "Changed content",
        })
        assert client.get(f"/prompts/{prompt_id}/versions").json()["total"] == 1

        # First restore of version 1
        response1 = client.post(f"/prompts/{prompt_id}/versions/1/restore")
        assert response1.status_code == 200
        assert client.get(f"/prompts/{prompt_id}/versions").json()["total"] == 2

        # Second restore of version 1
        response2 = client.post(f"/prompts/{prompt_id}/versions/1/restore")
        assert response2.status_code == 200
        assert client.get(f"/prompts/{prompt_id}/versions").json()["total"] == 3
