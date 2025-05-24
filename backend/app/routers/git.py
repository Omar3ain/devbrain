from fastapi import APIRouter, HTTPException
from typing import List, Dict
import subprocess
import os

router = APIRouter(
    prefix="/git",
    tags=["git"]
)

def get_staged_changes(path):
    try:
        os.chdir(path)
        result = subprocess.run(['git', 'diff'], capture_output=True, text=True, check=True)
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
    finally:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_git_changes(directory: str) -> List[Dict]:
    try:
        os.chdir(directory)
        
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        
        changes = []
        for line in result.stdout.splitlines():
            if line:
                status = line[:2]
                file_path = line[3:]
                
                change_type = "modified"
                if status.startswith('A'):
                    change_type = "added"
                elif status.startswith('D'):
                    change_type = "deleted"
                elif status.startswith('R'):
                    change_type = "renamed"
                
                changes.append({
                    "file_path": file_path,
                    "change_type": change_type
                })
        changes.append({"staged_changes": get_staged_changes(directory)})
        return changes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/changes")
def get_changes(directory: str):
    try:
        changes = get_git_changes(directory)
        return {
            "status": "success",
            "changes": changes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commit-message")
def generate_commit_message(directory: str):
    try:
        changes = get_git_changes(directory)
        
        # Generate a commit message based on the changes
        message_parts = []
        for change in changes:
            if change["change_type"] == "added":
                message_parts.append(f"Add {change['file_path']}")
            elif change["change_type"] == "modified":
                message_parts.append(f"Update {change['file_path']}")
            elif change["change_type"] == "deleted":
                message_parts.append(f"Remove {change['file_path']}")
        
        commit_message = "\n".join(message_parts)
        
        return {
            "status": "success",
            "message": commit_message,
            "changes": changes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 