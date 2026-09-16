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
        """Test that getting a non-existent prompt returns 404.
        
        NOTE: This test currently FAILS due to Bug #1!
        The API returns 500 instead of 404.
        """
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
        # Note: This might fail due to Bug #1
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
        
        # NOTE: This assertion will fail due to Bug #2!
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
        """Test that prompts are sorted newest first.
        
        NOTE: This test might fail due to Bug #3!
        """
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
        assert prompts[0]["title"] == "Second"  # Will fail until Bug #3 fixed

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
        assert response2.json()["title"] == "V2 Title"
    
    def test_versions_not_found(self, client: TestClient):
        response = client.get("/prompts/bad-id/versions")
        assert response.status_code == 404


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
        """Test deleting a collection that has prompts.
        
        NOTE: Bug #4 - prompts become orphaned after collection deletion.
        This test documents the current (buggy) behavior.
        After fixing, update the test to verify correct behavior.
        """
        # Create collection
        col_response = client.post("/collections", json=sample_collection_data)
        collection_id = col_response.json()["id"]
        
        # Create prompt in collection
        prompt_data = {**sample_prompt_data, "collection_id": collection_id}
        prompt_response = client.post("/prompts", json=prompt_data)
        prompt_id = prompt_response.json()["id"]
        
        # Delete collection
        client.delete(f"/collections/{collection_id}")
        
       # After the fix: the prompt still exists but is unassigned
        prompts = client.get("/prompts").json()["prompts"]
        assert len(prompts) == 1
        assert prompts[0]["collection_id"] is None