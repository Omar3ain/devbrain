from typing import List, Dict, Optional
import subprocess
from pydantic import BaseModel
import os
import logging
from git import Repo
from .ai_client import AIClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitChange(BaseModel):
    file_path: str
    change_type: str
    diff: Optional[str] = None

class GitAnalyzer:
    def __init__(self):
        self.ai_client = AIClient()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def generate_commit_message(self, changes: List[Dict]) -> Dict:
        if not changes:
            return {
                "status": "error",
                "detail": "No changes detected"
            }

        # Group changes by type
        modified_files = [c["file_path"] for c in changes if c["change_type"] == "modified"]
        added_files = [c["file_path"] for c in changes if c["change_type"] == "added"]
        deleted_files = [c["file_path"] for c in changes if c["change_type"] == "deleted"]

        # Prepare context for AI
        context = {
            "modified": modified_files,
            "added": added_files,
            "deleted": deleted_files
        }

        # Generate commit message using AI
        try:
            prompt = f"""As a senior software engineer, write a professional and concise git commit message for the following changes:

Modified files: {', '.join(modified_files) if modified_files else 'None'}
Added files: {', '.join(added_files) if added_files else 'None'}
Deleted files: {', '.join(deleted_files) if deleted_files else 'None'}

The commit message MUST follow this format:
type: message

Where type MUST be one of:
- feat: A new feature
- fix: A bug fix
- docs: Documentation changes
- style: Code style/formatting changes
- perf: Performance improvements
- test: Adding or modifying tests

Examples:
- feat: add user authentication system
- fix: resolve login timeout issue
- docs: update API documentation
- style: format code according to PEP8
- perf: optimize database queries
- test: add unit tests for auth module

The message should:
1. Start with a verb in present tense
2. Be clear and concise
3. Focus on the "why" rather than the "what"
4. Be professional and technical

Write only the commit message in the format "type: message", no additional text."""

            system_prompt = "You are a senior software engineer writing git commit messages."
            commit_message = self.ai_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=100
            )

            return {
                "status": "success",
                "message": commit_message,
                "changes": changes
            }

        except Exception as e:
            return {
                "status": "error",
                "detail": f"Failed to generate commit message: {str(e)}"
            } 