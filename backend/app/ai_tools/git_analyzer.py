from typing import List, Dict, Optional
from pydantic import BaseModel
from .ai_client import AIClient


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

    def generate_commit_message(self, changes: List[Dict], staged_changes: str) -> Dict:
        if not changes:
            return {
                "status": "error",
                "detail": "No changes detected"
            }

        # Group changes by type
        modified_files = [c["file_path"] for c in changes if c["change_type"] == "modified"]
        added_files = [c["file_path"] for c in changes if c["change_type"] == "added"]
        deleted_files = [c["file_path"] for c in changes if c["change_type"] == "deleted"]
        
        # Generate commit message using AI
        try:
            prompt = f"""
You are a senior software engineer. Your task is to generate a single, professional, and concise git commit message for a set of code changes.

You MUST follow these strict formatting rules:

----------------------------
FORMAT:
<type>: <message>

Valid types:
- feat: A new feature
- fix: A bug fix
- docs: Documentation changes
- style: Code style/formatting changes
- perf: Performance improvements
- test: Adding or modifying tests
----------------------------

The message must:
1. Start with a verb in present tense (e.g., add, fix, update, improve)
2. Be clear and concise (no longer than a single sentence)
3. Focus on the purpose or reason for the change — the "why"
4. **NOT** include file names, class names, variable names, or implementation details
5. **NOT** mention paths like `utils.py`, `GitAnalyzer`, etc.
6. Be the only content in the output — return exactly one line in the required format

Here are the changed files:
- Staged changes: {staged_changes}

Examples of good commit messages:
- feat: implement user authentication
- fix: prevent crash on empty login form
- docs: update README with setup instructions
- style: reformat code to follow PEP8
- perf: reduce memory usage in PDF parser
- test: add coverage for edge cases in API handler

❌ Bad examples (do NOT do this):
- fix: resolve issue in GitAnalyzer class
- feat: add EmailService to notifications.py
- fix: change logic in settings.py

✅ Good alternatives for the above:
- fix: address parsing issue in git analysis
- feat: add service to handle user email notifications
- fix: improve configuration validation

Checklist before returning:
- [ ] Is the message in the format "<type>: <message>"?
- [ ] Does it use one of the allowed types?
- [ ] Is it a single, clear sentence?
- [ ] Does it avoid class names, filenames, or paths?

Now generate the commit message below. **Return ONLY the commit message.**
"""

            system_prompt = "You are a senior software engineer. Your only job is to write accurate, clean, and concise git commit messages. Always follow the required format and never output anything else."
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