from fastapi import APIRouter, HTTPException
from typing import List, Dict
import subprocess
import os
from app.ai_tools.git_analyzer import GitAnalyzer

router = APIRouter(
    prefix="/git",
    tags=["git"]
)

def get_staged_changes(path: str) -> str:
    try:
        os.chdir(path)
        result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True, check=True)
        
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
        
        return changes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/changes")
def get_changes(directory: str):
    try:
        changes = get_git_changes(directory)
        return {
            "status": "success",
            "changes": changes,
            "staged_changes": get_staged_changes(directory)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commit-message")
def generate_commit_message(directory: str):
    try:
        if not os.path.exists(directory):
            raise HTTPException(status_code=400, detail=f"Directory not found: {directory}")
        
        with GitAnalyzer() as analyzer:
            result = analyzer.generate_commit_message(get_git_changes(directory), get_staged_changes(directory))
            if result["status"] == "error":
                raise HTTPException(status_code=500, detail=result)
            
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 