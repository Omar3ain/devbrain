from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
from .ai_client import AIClient
from app.models.command import Command

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandAnalyzer:
    def __init__(self):
        self.ai_client = AIClient()

    def search_commands(self, query: str, db: Session) -> Dict:
        """
        Search for commands using natural language query.
        
        Args:
            query (str): The natural language query
            db (Session): Database session
            
        Returns:
            Dict: Search results with AI analysis
        """
        try:
            # Get all commands from the last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_commands = db.query(Command).filter(
                Command.timestamp > yesterday
            ).order_by(Command.timestamp.desc()).all()
            
            if not recent_commands:
                return {
                    "status": "success",
                    "message": "No commands found in the last 24 hours",
                    "commands": []
                }
            
            # Format commands for AI context
            commands_context = []
            for cmd in recent_commands:
                commands_context.append({
                    "command": cmd.command,
                    "timestamp": cmd.timestamp.isoformat(),
                    "directory": cmd.directory,
                    "git_branch": cmd.git_branch
                })
            
            # Create AI prompt
            prompt = f"""Given the following user query and a list of recent commands, find the most relevant command(s) that match the query.

User Query: {query}

Recent Commands:
{commands_context}

Instructions:
1. Analyze the user's query to understand what they're looking for
2. Consider time references (e.g., "last night", "yesterday", "this morning")
3. Consider command patterns (e.g., "list files" might be "ls")
4. Return the most relevant command(s) that match the query
5. If multiple commands match, return the most recent one
6. If no commands match, explain why

Format your response as:
Command: <the actual command>
Time: <when it was run>
Directory: <where it was run>
Explanation: <why this command matches the query>"""

            system_prompt = "You are a helpful assistant that finds relevant terminal commands based on natural language queries."
            ai_response = self.ai_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=200
            )
            
            # Parse the command from the response
            command = None
            if "Command:" in ai_response:
                command_line = ai_response.split("Command:")[1].split("\n")[0].strip()
                # Remove quotes if present
                command = command_line.strip("'\"")
            
            return {
                "status": "success",
                "message": ai_response,
                "command": command,  # The command for easy copy-paste
                "commands": commands_context
            }
            
        except Exception as e:
            logger.error(f"Error in command search: {str(e)}")
            raise 