import sys
import os
import asyncio
from dotenv import load_dotenv

# Add project root to sys.path to allow importing prompts and tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env explicitly if running independently
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    env_file = os.path.join(project_root, ".env")
    load_dotenv(env_file)
    # Compatibility logic for API Keys
    if os.getenv("ARK_API_KEY") and not os.getenv("MODEL_AGENT_API_KEY"):
        os.environ["MODEL_AGENT_API_KEY"] = os.getenv("ARK_API_KEY")

from veadk import Agent, Runner
from veadk.memory.short_term_memory import ShortTermMemory
from prompts import DIRECTOR_AGENT_PROMPT

director_agent = Agent(
    name="director_agent",
    description="项目总导演，负责分析用户需求，确定影片基调、创意简报和统筹工作流",
    instruction=DIRECTOR_AGENT_PROMPT,
    model_name="doubao-seed-1-8-251228" # 指定使用推理能力较强的模型
)

if __name__ == "__main__":
    async def main():
        runner = Runner(
            agent=director_agent,
            short_term_memory=ShortTermMemory(),
            app_name="director_agent_test",
            user_id="test_user"
        )
        print("🎬 Testing Director Agent...")
        response = await runner.run(
            messages="Generate a cyberpunk style manga about a courier girl delivering a mysterious package in Neo-Tokyo."
        )
        print("✅ Response:", response)

    asyncio.run(main())
