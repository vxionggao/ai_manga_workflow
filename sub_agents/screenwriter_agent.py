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
    if os.getenv("ARK_API_KEY") and not os.getenv("MODEL_AGENT_API_KEY"):
        os.environ["MODEL_AGENT_API_KEY"] = os.getenv("ARK_API_KEY")

from veadk import Agent, Runner
from veadk.memory.short_term_memory import ShortTermMemory
from prompts import SCREENWRITER_AGENT_PROMPT

screenwriter_agent = Agent(
    name="screenwriter_agent",
    description="专业编剧，负责将创意简报转化为分场剧本",
    instruction=SCREENWRITER_AGENT_PROMPT,
    model_name="doubao-seed-1-8-251228" # 使用与导演相同的推理模型
)

if __name__ == "__main__":
    async def main():
        runner = Runner(
            agent=screenwriter_agent,
            short_term_memory=ShortTermMemory(),
            app_name="screenwriter_agent_test",
            user_id="test_user"
        )
        print("🎬 Testing Screenwriter Agent...")
        # Provide a sample creative brief
        sample_input = "Title: Neo-Tokyo Courier\nGenre: Cyberpunk\nPlot: A courier girl named Kaito delivers a package containing an AI chip that can overthrow the megacorp."
        response = await runner.run(messages=sample_input)
        print("✅ Response:", response)

    asyncio.run(main())
