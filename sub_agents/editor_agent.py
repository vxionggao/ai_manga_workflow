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
from prompts import EDITOR_AGENT_PROMPT
from tools.file_tools import download_files

from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

# MCP Tool for Video Clipping
import shutil

# Dynamically find npx
npx_path = shutil.which("npx")
if not npx_path:
    # Fallback for common locations if not in PATH
    common_paths = [
        "/usr/local/bin/npx",
        "/opt/homebrew/bin/npx",
        os.path.expanduser("~/.nvm/versions/node/v*/bin/npx"), # Basic wildcard logic needed if we were to implement full search
    ]
    # For now, just try to find it in the current python env's bin (if conda installed nodejs)
    python_bin = os.path.dirname(sys.executable)
    potential_npx = os.path.join(python_bin, "npx")
    if os.path.exists(potential_npx):
        npx_path = potential_npx

if not npx_path:
    print("Warning: npx not found. MCP tool might fail.")
    npx_path = "npx" # Last resort

# Get current python environment bin path (where we symlinked ffmpeg)
python_bin_dir = os.path.dirname(sys.executable)
new_env = os.environ.copy()
# Prepend python bin to PATH to ensure our ffmpeg is found first
new_env["PATH"] = f"{python_bin_dir}:{new_env.get('PATH', '')}"

server_parameters = StdioServerParameters(
    command=npx_path,
    args=["-y", "@pickstar-2002/video-clip-mcp@latest"],
    env=new_env
)
mcpTool = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=server_parameters, timeout=600.0
    ),
    errlog=None,
)

editor_agent = Agent(
    name="editor_agent",
    description="剪辑师，负责视频片段的拼接与后期处理",
    instruction=EDITOR_AGENT_PROMPT,
    model_name="doubao-seed-1-8-251228", # 使用推理模型规划剪辑脚本
    tools=[mcpTool, download_files]
)

if __name__ == "__main__":
    async def main():
        runner = Runner(
            agent=editor_agent,
            short_term_memory=ShortTermMemory(),
            app_name="editor_agent_test",
            user_id="test_user"
        )
        print("🎬 Testing Editor Agent...")
        sample_input = "Combine these 3 video clips into a 15-second trailer. Clip1: ..., Clip2: ..., Clip3: ..."
        response = await runner.run(messages=sample_input)
        print("✅ Response:", response)

    asyncio.run(main())
