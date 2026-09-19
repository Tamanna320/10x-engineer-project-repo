# Agent Effect Note

## Purpose

This document provides a concrete example of how the PromptLab `.continuerules` file affected AI-generated output.

The same prompt was given to Continue before and after the project-specific rules were enabled.

## Rule That Was Tested

The `.continuerules` file contains project-specific development standards, including:

* Reuse existing project patterns before introducing a new approach.
* Use Pydantic models for API request and response data.
* Keep API route handling in `backend/app/api.py`.
* Keep storage logic in `backend/app/storage.py`.
* Use appropriate HTTP status codes and clear error messages.
* Use Google-style docstrings with `Args`, `Returns`, and `Raises`.
* Do not invent APIs, models, fields, or project behavior.
* Add or update tests when application behavior changes.

## Test Prompt

The following prompt was given to Continue:

> In the PromptLab project, create a new API endpoint for creating a prompt.
>
> Use the existing project structure and patterns.
>
> Do not modify any files. Just show me the code you would generate.

## Before `.continuerules`

Before the project-specific rules were active, Continue generated a response that mainly explained that `POST /prompts` already existed and then provided the existing `create_prompt` implementation.

The response included explanations such as:

> "A `POST /prompts` endpoint already exists in the current `backend/app/api.py`."

It also explained how the generated endpoint followed the existing project patterns, including the placement, decorator, validation, model construction, storage call, and docstring.

However, the response did not explicitly organize the output as a rule-by-rule compliance check.

## After `.continuerules`

After enabling `.continuerules`, Continue generated the same existing endpoint because the rules instructed it to inspect the existing project before generating code and not invent APIs or project behavior.

The response also added a dedicated **"Rule-by-rule compliance"** section.

For example, it explicitly connected the generated code to project rules:

| Rule                                          | How the code complies                                           |
| --------------------------------------------- | --------------------------------------------------------------- |
| Keep API route handling in `api.py`           | Route lives in the Prompt Endpoints section.                    |
| Use Pydantic models for request/response data | `PromptCreate` is used for input and `Prompt` for the response. |
| Keep storage logic in `storage.py`            | Persistence is handled by `storage.create_prompt()`.            |
| Reuse existing patterns                       | The endpoint follows the existing project patterns.             |
| No new dependencies                           | Existing imports are reused.                                    |
| Existing error-handling patterns              | The existing `HTTPException` pattern is preserved.              |
| Google-style docstrings                       | `Args`, `Returns`, and `Raises` sections are included.          |
| snake_case naming                             | Existing Python naming conventions are followed.                |

## What Changed

The generated endpoint itself did not change significantly because the project already contained a `POST /prompts` endpoint and the existing implementation already followed the project's conventions.

The observable change was in how Continue reasoned about and presented the generated output.

Before the rules were enabled, Continue explained the existing implementation and why it matched the project.

After the rules were enabled, Continue explicitly checked the generated code against the project-specific rules and presented a rule-by-rule compliance table.

This demonstrates that the `.continuerules` file influenced the AI's generated response by making the project-specific conventions explicit during code generation and review.

## Conclusion

The experiment shows that project-specific instructions can guide Continue to:

1. Inspect existing project code before proposing changes.
2. Avoid inventing duplicate endpoints or project behavior.
3. Reuse existing FastAPI, Pydantic, storage, error-handling, and documentation patterns.
4. Explicitly relate generated code to the project's development rules.

The endpoint was not duplicated or unnecessarily changed because the `.continuerules` file instructed the agent to preserve existing project behavior and reuse established patterns.
