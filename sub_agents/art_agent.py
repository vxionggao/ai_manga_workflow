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
from prompts import ART_AGENT_PROMPT
from tools.veadk_wrappers import image_generate

# 注意：虽然这里指定了 model，但 veadk 的 Agent 默认是处理文本的。
# 真正的生图逻辑通常需要封装成一个 Tool，由 Agent 调用。
# 这里的 model 参数用于指导 Agent 如何生成生图提示词（Prompt Engineering），而非直接生图。
# 实际生图动作由 Agent 调用的工具（如 image_gen_tool）完成，该工具内部会调用 seedream-4.5
art_agent = Agent(
    name="art_agent",
    description="美术指导，负责设计视觉风格并生成画面",
    instruction=ART_AGENT_PROMPT,
    model_name="doubao-seed-1-8-251228", # 使用推理模型来生成高质量的生图 Prompt
    tools=[image_generate] # 绑定生图工具
)

if __name__ == "__main__":
    async def main():
        runner = Runner(
            agent=art_agent,
            short_term_memory=ShortTermMemory(),
            app_name="art_agent_test",
            user_id="test_user"
        )
        print("🎬 Testing Art Agent...")
        sample_input = "Scene 1: Kaito riding her hover-bike through neon-lit streets. High angle shot. Cyberpunk style."
        response = await runner.run(messages=sample_input)
        print("✅ Response:", response)

    asyncio.run(main())
