from typing import List, Dict, Optional
import subprocess
from pydantic import BaseModel
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
from git import Repo

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class GitChange(BaseModel):
    file_path: str
    change_type: str
    diff: Optional[str] = None

class GitAnalyzer:
    def __init__(self, directory: str):
        self.directory = os.path.abspath(directory)
        self.original_dir = os.getcwd()
        try:
            self.repo = Repo(self.directory)
            logger.info(f"Initialized Git repo at {self.directory}")
        except Exception as e:
            logger.error(f"Failed to initialize Git repo: {str(e)}")
            raise ValueError(f"Invalid Git repository at {self.directory}")
            
        api_key = os.getenv("OPEN_ROUTER_KEY")
        if not api_key:
            raise ValueError("OPEN_ROUTER_KEY environment variable is not set")
        
        # Configure OpenAI client for OpenRouter
        # self.client = OpenAI(
        #     base_url="https://openrouter.ai/api/v1",
        #     api_key=api_key,
        #     default_headers={
        #         "X-Title": "DevBrain Git Analyzer"
        #     }
        # )

    def __enter__(self):
        os.chdir(self.directory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_dir)

    def get_changes(self) -> List[GitChange]:
        changes = []
        
        try:
            # Get staged changes
            for item in self.repo.index.diff('HEAD'):
                file_path = item.a_path
                change_type = "modified"  # GitPython doesn't distinguish between M/A/D in diff
                
                # Get the diff
                diff = self.repo.git.diff('HEAD', file_path)
                logger.info(f"Diff for {file_path}: {diff}...")

                changes.append(GitChange(
                    file_path=file_path,
                    change_type=change_type,
                    diff=diff
                ))
                
            logger.info(f"Total staged changes detected: {len(changes)}")
            return changes
        except Exception as e:
            logger.error(f"Error getting changes: {str(e)}")
            raise ValueError(f"Failed to get Git changes: {str(e)}")

    def generate_commit_message(self) -> Dict:
        changes = self.get_changes()
        if not changes:
            logger.warning("No changes detected")
            return {
                "status": "error",
                "detail": "No changes detected"
            }

        # Group changes by type
        modified_files = [c.file_path for c in changes if c.change_type == "modified"]
        added_files = [c.file_path for c in changes if c.change_type == "added"]
        deleted_files = [c.file_path for c in changes if c.change_type == "deleted"]

        logger.info(f"Modified files: {modified_files}")
        logger.info(f"Added files: {added_files}")
        logger.info(f"Deleted files: {deleted_files}")

        # Prepare context for AI
        context = {
            "modified": modified_files,
            "added": added_files,
            "deleted": deleted_files,
            "diffs": {c.file_path: c.diff for c in changes if c.diff}
        }

        # Generate commit message using OpenRouter
        try:
            prompt = f"""As a senior software engineer, write a professional and concise git commit message for the following changes:

Modified files: {', '.join(modified_files) if modified_files else 'None'}
Added files: {', '.join(added_files) if added_files else 'None'}
Deleted files: {', '.join(deleted_files) if deleted_files else 'None'}

The commit message should:
1. Start with a verb in present tense
2. Be clear and concise
3. Focus on the "why" rather than the "what"
4. Follow conventional commit format if applicable
5. Be professional and technical

Write only the commit message, no additional text."""

            logger.info("Sending request to OpenRouter API")
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-opus:beta",  # Using Claude 3 Opus via OpenRouter
                messages=[
                    {"role": "system", "content": "You are a senior software engineer writing git commit messages."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )

            commit_message = response.choices[0].message.content.strip()
            logger.info(f"Generated commit message: {commit_message}")

            return {
                "status": "success",
                "message": commit_message,
                "changes": [change.dict() for change in changes]
            }

        except Exception as e:
            logger.error(f"Error generating commit message: {str(e)}")
            return {
                "status": "error",
                "detail": f"Failed to generate commit message: {str(e)}"
            } 