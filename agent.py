import asyncio
import os
import sys
from dotenv import load_dotenv

# Load .env explicitly
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(current_dir, ".env")
load_dotenv(env_file)

# Compatibility: If user provided ARK_API_KEY but not MODEL_AGENT_API_KEY, copy it over
if os.getenv("ARK_API_KEY") and not os.getenv("MODEL_AGENT_API_KEY"):
    os.environ["MODEL_AGENT_API_KEY"] = os.getenv("ARK_API_KEY")

from agentkit.apps import AgentkitAgentServerApp
from veadk import Agent  # Import generic Agent for the router
from veadk.agents.sequential_agent import SequentialAgent
from veadk import Runner
from veadk.memory.short_term_memory import ShortTermMemory

# Add current directory to Python path to support sub_agents imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sub_agents.director_agent import director_agent
from sub_agents.screenwriter_agent import screenwriter_agent
from sub_agents.art_agent import art_agent
from sub_agents.motion_agent import motion_agent
from sub_agents.editor_agent import editor_agent
from sub_agents.badcase_optimizer_agent import badcase_optimizer_agent

# 1. 美术生成
# 原 LoopAgent 逻辑已移除，恢复为单一 Art Agent 执行
# Badcase 优化将由用户在外部手动介入（例如在 Review 阶段调用 badcase_optimizer_agent）
# 此处只需定义标准流程

# 2. 动效生成 (同理)

# 3. 主工作流 (保持为 SequentialAgent)
workflow_agent = SequentialAgent(
    name="manga_workflow_agent",
    description="全自动 AI 漫剧生成工作流",
    instruction="""
    你是一个自动化的漫剧制作系统。
    请严格按照以下顺序执行任务：
    1. 导演 (Director): 分析需求，确定创意简报。
    2. 编剧 (Screenwriter): 根据简报生成分场剧本。
    3. 美术 (Art): 根据剧本生成角色和场景图片。
    4. 动效 (Motion): 为图片添加动态效果。
    5. 剪辑 (Editor): 将视频片段拼接成最终成片。
    """,
    sub_agents=[
        director_agent,
        screenwriter_agent,
        art_agent,
        motion_agent,
        editor_agent
    ]
)

# 4. 顶层路由 Agent
root_router_agent = Agent(
    name="root_router",
    description="AI 漫剧系统总控",
    instruction="""
    你是 AI 漫剧系统的总控 Agent。
    根据用户的意图，将任务路由给合适的子 Agent：
    
    - 如果用户想从头生成一个新的漫剧/视频/项目，路由给 `manga_workflow_agent`。
    - 如果用户想优化、修复或重绘已有的图片或视频（例如“优化第4个视频”），路由给 `badcase_optimizer_agent`。
    """,
    sub_agents=[
        workflow_agent,
        badcase_optimizer_agent
    ]
)

root_agent = root_router_agent

# Create ShortTermMemory instance
short_term_memory = ShortTermMemory(backend="local")

# Create Agent Server App
agent_server_app = AgentkitAgentServerApp(
    agent=root_agent,
    short_term_memory=short_term_memory,
)

# Keep get_runner for local main.py usage if needed, but updated to use shared memory
def get_runner():
    runner = Runner(
        agent=root_agent,
        short_term_memory=short_term_memory,
        app_name="ai_manga_app",
        user_id="demo_user"
    )
    return runner

if __name__ == "__main__":
    # Start the HTTP server
    agent_server_app.run(host="0.0.0.0", port=8000)
