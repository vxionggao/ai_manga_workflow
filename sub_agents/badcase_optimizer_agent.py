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
from veadk.knowledgebase.knowledgebase import KnowledgeBase
from prompts import BADCASE_OPTIMIZER_AGENT_PROMPT
from tools.veadk_wrappers import video_generate, image_generate

# 配置知识库：Viking 向量数据库
knowledge_collection_name = os.getenv("DATABASE_VIKING_COLLECTION", "")
knowledge = None
if knowledge_collection_name:
    print(f"[BadcaseAgent] Initializing KnowledgeBase with VikingDB collection: {knowledge_collection_name}")
    try:
        knowledge = KnowledgeBase(backend="viking", index=knowledge_collection_name)
    except Exception as e:
        print(f"[BadcaseAgent] Failed to initialize KnowledgeBase: {e}")

# 定义一个工具来通知 LoopAgent 结束循环
# 当 Badcase Agent 认为质量合格（PASS）时，调用此工具
def quality_check_pass() -> str:
    """
    Call this tool when the quality check is passed (no defects found).
    This will signal the workflow to proceed to the next step.
    """
    # 在 LoopAgent 的机制中，调用特定的 tool (如 exit_tool) 会触发循环终止
    # 这里我们返回一个特定标记，LoopAgent 内部需要配置这个 tool 为 exit_tool
    return "QUALITY_PASS"

badcase_optimizer_agent = Agent(
    name="badcase_optimizer_agent",
    description="质量检测员，负责识别并修复生成缺陷",
    instruction=BADCASE_OPTIMIZER_AGENT_PROMPT,
    model_name="doubao-seed-1-8-251228",
    tools=[quality_check_pass, video_generate, image_generate],
    knowledgebase=knowledge
)

if __name__ == "__main__":
    async def main():
        runner = Runner(
            agent=badcase_optimizer_agent,
            short_term_memory=ShortTermMemory(),
            app_name="badcase_optimizer_agent_test",
            user_id="test_user"
        )
        print("🎬 Testing Badcase Optimizer Agent...")
        sample_input = "Check this image for anatomy errors: [image_url]"
        response = await runner.run(messages=sample_input)
        print("✅ Response:", response)

    asyncio.run(main())
