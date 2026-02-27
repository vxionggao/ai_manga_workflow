import asyncio
import os
from dotenv import load_dotenv

# Load environment variables (API Keys, etc.) before importing other modules
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(current_dir, ".env")
load_dotenv(env_file)

from agent import root_agent
from veadk import Runner
from veadk.memory.short_term_memory import ShortTermMemory

app_name = "ai_manga_app"
user_id = "demo_user"
session_id = "demo_session"

short_term_memory = ShortTermMemory()

runner = Runner(
    agent=root_agent,
    short_term_memory=short_term_memory,
    app_name=app_name,
    user_id=user_id,
)

async def main():
    print("🎬 AI Manga Workflow Starting...")
    
    # Define user input
    user_prompt = "Generate a cyberpunk style manga about a courier girl delivering a mysterious package in Neo-Tokyo."
    
    # Run the workflow
    print(f"User Request: {user_prompt}")
    print("-" * 50)
    
    try:
        response = await runner.run(
            messages=user_prompt,
            session_id=session_id
        )
        
        print("-" * 50)
        print("✅ Workflow Completed!")
        print("Final Output:", response)
        
    except Exception as e:
        print(f"❌ Workflow Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
