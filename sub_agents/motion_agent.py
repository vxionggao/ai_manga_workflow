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
from prompts import MOTION_AGENT_PROMPT
from tools.veadk_wrappers import video_generate

motion_agent = Agent(
    name="motion_agent",
    description="动效专家，负责为静态画面添加动态效果",
    instruction=MOTION_AGENT_PROMPT,
    model_name="doubao-seed-1-8-251228", # 使用推理模型规划运镜参数
    tools=[video_generate] # 绑定生视频工具
)

if __name__ == "__main__":
    async def main():
        runner = Runner(
            agent=motion_agent,
            short_term_memory=ShortTermMemory(),
            app_name="motion_agent_test",
            user_id="test_user"
        )
        print("🎬 Testing Motion Agent...")
        image_url = "https://manju-test.tos-cn-beijing.volces.com/upload/sample_image.jpeg"
        sample_input = f"Apply a 'pan left' motion to this image: {image_url}. Make it a cinematic shot."
        response = await runner.run(messages=sample_input)
        print("✅ Response:", response)

    asyncio.run(main())
