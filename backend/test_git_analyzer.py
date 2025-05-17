from app.ai_tools.git_analyzer import GitAnalyzer
import os
import json

def main():
    # Get the current directory
    current_dir = os.getcwd()
    print(f"\nCurrent directory: {current_dir}")
    
    # Create GitAnalyzer instance
    with GitAnalyzer(current_dir) as analyzer:
        # Get changes
        changes = analyzer.get_changes()
        print("\nChanges detected:")
        for change in changes:
            print(f"\nFile: {change.file_path}")
            print(f"Type: {change.change_type}")
            if change.diff:
                print(f"Diff preview: {change.diff[:200]}...")
            print("-" * 50)
        
        # Print raw changes data
        print("\nRaw changes data:")
        print(json.dumps([change.dict() for change in changes], indent=2))
        
        # Generate commit message
        result = analyzer.generate_commit_message()
        print("\nGenerated commit message:")
        if result["status"] == "success":
            print(result["message"])
        else:
            print(f"Error: {result['detail']}")

if __name__ == "__main__":
    main() 