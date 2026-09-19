"""In-memory storage for PromptLab

This module provides simple in-memory storage for prompts and collections.
In a production environment, this would be replaced with a database.
"""

from typing import Dict, List, Optional
from app.models import Prompt, Collection, PromptVersion


class Storage:
    """In-memory storage for prompts, collections, and prompt versions.

    Keeps all data in process memory using dictionaries. This is intended for
    development and testing; in a production environment it would be replaced
    with a database-backed implementation.

    Attributes:
        _prompts: Mapping of prompt IDs to Prompt objects.
        _collections: Mapping of collection IDs to Collection objects.
        _versions: Mapping of prompt IDs to their list of PromptVersion objects.
    """

    def __init__(self):
        """Initialize the storage with empty prompt, collection, and version stores."""
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}
        self._versions: Dict[str, List[PromptVersion]] = {}
    
    # ============== Prompt Operations ==============
    
    def create_prompt(self, prompt: Prompt) -> Prompt:
        """Store a new prompt.

        If a prompt with the same ID already exists, it is overwritten.

        Args:
            prompt: The Prompt object to store. Its ``id`` is used as the key.

        Returns:
            The Prompt object that was stored.
        """
        self._prompts[prompt.id] = prompt
        return prompt
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Retrieve a prompt by its ID.

        Args:
            prompt_id: The unique identifier of the prompt.

        Returns:
            The Prompt object if found, otherwise None.
        """
        return self._prompts.get(prompt_id)
    
    def get_all_prompts(self) -> List[Prompt]:
        """Retrieve all stored prompts.

        Returns:
            A list of all Prompt objects currently in storage. The list is
            empty if no prompts have been stored.
        """
        return list(self._prompts.values())
    
    def update_prompt(self, prompt_id: str, prompt: Prompt) -> Optional[Prompt]:
        """Replace an existing prompt.

        Args:
            prompt_id: The unique identifier of the prompt to update.
            prompt: The new Prompt object to store under ``prompt_id``.

        Returns:
            The updated Prompt object if a prompt with ``prompt_id`` exists,
            otherwise None.
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt and its version history.

        Args:
            prompt_id: The unique identifier of the prompt to delete.

        Returns:
            True if the prompt existed and was deleted, False otherwise.
        """
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            self._versions.pop(prompt_id, None)
            return True
        return False
    
    # ============== Collection Operations ==============
    
    def create_collection(self, collection: Collection) -> Collection:
        """Store a new collection.

        If a collection with the same ID already exists, it is overwritten.

        Args:
            collection: The Collection object to store. Its ``id`` is used
                as the key.

        Returns:
            The Collection object that was stored.
        """
        self._collections[collection.id] = collection
        return collection
    
    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Retrieve a collection by its ID.

        Args:
            collection_id: The unique identifier of the collection.

        Returns:
            The Collection object if found, otherwise None.
        """
        return self._collections.get(collection_id)
    
    def get_all_collections(self) -> List[Collection]:
        """Retrieve all stored collections.

        Returns:
            A list of all Collection objects currently in storage. The list
            is empty if no collections have been stored.
        """
        return list(self._collections.values())
    
    def delete_collection(self, collection_id: str) -> bool:
        """Delete a collection.

        Prompts that belong to the collection are not deleted.

        Args:
            collection_id: The unique identifier of the collection to delete.

        Returns:
            True if the collection existed and was deleted, False otherwise.
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False
    
    def get_prompts_by_collection(self, collection_id: str) -> List[Prompt]:
        """Retrieve all prompts that belong to a collection.

        Args:
            collection_id: The unique identifier of the collection.

        Returns:
            A list of Prompt objects whose ``collection_id`` matches the given
            ID. The list is empty if no prompts belong to the collection.
        """
        return [p for p in self._prompts.values() if p.collection_id == collection_id]

        # ============== Version Operations ==============
    
    def save_version(self, prompt_id: str, version: PromptVersion) -> None:
        """Append a version to a prompt's version history.

        Creates an empty version history for the prompt first if one does
        not exist.

        Args:
            prompt_id: The unique identifier of the prompt the version
                belongs to.
            version: The PromptVersion object to append.

        Returns:
            None.
        """
        if prompt_id not in self._versions:
            self._versions[prompt_id] = []
        self._versions[prompt_id].append(version)
    
    def get_versions(self, prompt_id: str) -> List[PromptVersion]:
        """Retrieve the version history of a prompt.

        Args:
            prompt_id: The unique identifier of the prompt.

        Returns:
            A list of PromptVersion objects for the prompt, in the order they
            were saved. The list is empty if the prompt has no saved versions.
        """
        return self._versions.get(prompt_id, [])
    
    def get_version(self, prompt_id: str, version_number: int) -> Optional[PromptVersion]:
        """Retrieve a specific version of a prompt by version number.

        Args:
            prompt_id: The unique identifier of the prompt.
            version_number: The version number to look up.

        Returns:
            The PromptVersion with the matching version number if found,
            otherwise None.
        """
        for v in self.get_versions(prompt_id):
            if v.version == version_number:
                return v
        return None
    
    # ============== Utility ==============
    
    def clear(self):
        """Remove all prompts, collections, and versions from storage.

        Returns:
            None.
        """
        self._prompts.clear()
        self._collections.clear()
        self._versions.clear()


# Global storage instance
storage = Storage()
