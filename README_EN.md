# AI Manga Workflow - Intelligent Manga Video Generation

A fully automated AI manga video generation system built on **Volcengine VeADK** and **AgentKit**, demonstrating multi-agent collaboration for complex creative tasks.

## Overview

This system establishes a complete production pipeline for Manga Videos. Through the collaborative work of multiple specialized Agents, it transforms a user's brief creative idea into a complete manga video, including storyboard scripts, character drawings, motion effects generation, and video editing. It also features a quality optimization mechanism to support refined adjustments of the generated results.

## Core Features

- **End-to-End Automation**: One-stop generation from idea to final video.
- **Hierarchical Architecture**:
  - **Root Router**: The master controller responsible for task distribution (New Project vs. Optimization/Repair).
  - **Sequential Workflow**: Sequentially executes the core production process (Director -> Screenwriter -> Art -> Motion -> Editor).
- **Specialized Division of Labor**: Each Agent focuses on tasks in a specific domain (e.g., Screenwriter focuses on scripts, Art Agent focuses on visuals).
- **Tool Integration**: Integrates AI capabilities such as Text-to-Image (Image Generation) and Image-to-Video (Video Generation).

## Agent Architecture

![Architecture](./img/whiteboard_exported_image.png)

```text
User Request
    ↓
Root Router Agent (Master Controller)
    ├── Manga Workflow Agent (Core Production Pipeline - Sequential)
    │   ├── Director Agent (Creative Brief & Coordination)
    │   ├── Screenwriter Agent (Storyboard Creation)
    │   ├── Art Agent (Character & Scene Drawing)
    │   ├── Motion Agent (Motion Video Generation)
    │   └── Editor Agent (Video Concatenation & Final Cut)
    │
    └── Badcase Optimizer Agent (Optimizer - Independent Task)
        └── Repairs and optimizes specific shots or frames
```

### Core Components

| Component | Description |
| - | - |
| **Main Agent** | [agent.py](agent.py) - Defines the Root Router and Sequential Workflow, orchestrating the entire process. |
| **Sub Agents** | [sub_agents/](sub_agents/) - Implementations of all specialized sub-agents. |
| **- Director** | [sub_agents/director_agent.py](sub_agents/director_agent.py) - Responsible for creative planning. |
| **- Screenwriter** | [sub_agents/screenwriter_agent.py](sub_agents/screenwriter_agent.py) - Responsible for scriptwriting. |
| **- Art** | [sub_agents/art_agent.py](sub_agents/art_agent.py) - Responsible for visual generation. |
| **- Motion** | [sub_agents/motion_agent.py](sub_agents/motion_agent.py) - Responsible for motion effects. |
| **- Editor** | [sub_agents/editor_agent.py](sub_agents/editor_agent.py) - Responsible for editing and synthesis. |
| **- Optimizer** | [sub_agents/badcase_optimizer_agent.py](sub_agents/badcase_optimizer_agent.py) - Responsible for quality repair. |
| **Tools** | [tools/](tools/) - Encapsulates calls to external tools like image and video generation. |
| **Prompts** | [prompts.py](prompts.py) - Centralized management of System Prompts for each Agent. |
| **Run Script** | [main.py](main.py) - Local execution script to run the workflow directly. |

## Directory Structure

```bash
ai_manga_workflow/
├── agent.py                      # Main Agent definition & HTTP Server entry point
├── main.py                       # Local execution script (CLI mode)
├── prompts.py                    # Prompt definitions for each Agent
├── sub_agents/                   # Sub-agent implementations
│   ├── director_agent.py
│   ├── screenwriter_agent.py
│   ├── art_agent.py
│   ├── motion_agent.py
│   ├── editor_agent.py
│   └── badcase_optimizer_agent.py
├── tools/                        # Tool functions
│   ├── image_gen.py
│   ├── video_gen.py
│   └── ...
├── requirements.txt              # Python dependency list
├── .env                          # Environment variable configuration (create manually)
└── README.md                     # Project documentation
```

## Local Execution

### Prerequisites

**1. Activate Volcengine Ark Model Service:**
- Visit [Volcengine Ark Console](https://exp.volcengine.com/ark?mode=chat)
- Activate necessary model services (e.g., Doubao-pro, Seedream, Seedance, etc.).

**2. Obtain Volcengine Access Credentials:**
- Get Access Key (AK) and Secret Key (SK).
- Get Ark API Key.

### Install Dependencies

Python 3.10+ is recommended.

```bash
# Enter project directory
cd ai_manga_workflow

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root directory and fill in the following configuration:

```ini
# Volcengine Authentication
VOLCENGINE_ACCESS_KEY=your_ak
VOLCENGINE_SECRET_KEY=your_sk
ARK_API_KEY=your_ark_api_key

# Model Endpoint Configuration
# For text reasoning (Director, Screenwriter, etc.)
MODEL_ENDPOINT_TEXT=your_doubao_pro_endpoint
# For image generation (Art Agent)
MODEL_ENDPOINT_IMAGE=your_seedream_endpoint
# For video generation (Motion Agent)
MODEL_ENDPOINT_VIDEO=your_seedance_endpoint

# TOS Object Storage Configuration (for storing generated assets)
TOS_ENDPOINT=tos-cn-beijing.volces.com
TOS_REGION=cn-beijing
TOS_BUCKET_NAME=your_bucket_name
```

### Running the Workflow

#### Method 1: Direct CLI Execution (Recommended for Debugging)

Run `main.py` directly to simulate a user request and execute the full pipeline.

```bash
python main.py
```

Default request example (can be modified in `main.py`):
> "Generate a cyberpunk style manga about a courier girl delivering a mysterious package in Neo-Tokyo."

#### Method 2: Start HTTP Server

Run `agent.py` to start an HTTP service compatible with the AgentKit protocol.

```bash
python agent.py
# The service will listen on http://0.0.0.0:8000
```

## AgentKit Deployment

This project supports deployment to cloud environments via AgentKit.

### 1. Configure Deployment Parameters

```bash
# Initialize configuration
agentkit config \
    --agent_name "ai_manga_workflow" \
    --entry_point "agent.py" \
    --launch_type "cloud" \
    --image_tag "v1.0.0" \
    --region "cn-beijing" \
    --tos_bucket "$DATABASE_TOS_BUCKET" \
    --runtime_envs ARK_API_KEY="$ARK_API_KEY" \
    --runtime_envs VOLCENGINE_ACCESS_KEY="$VOLCENGINE_ACCESS_KEY" \
    --runtime_envs VOLCENGINE_SECRET_KEY="$VOLCENGINE_SECRET_KEY" \
    --runtime_envs MODEL_AGENT_API_KEY="$MODEL_AGENT_API_KEY" \
    --runtime_envs MODEL_IMAGE_NAME="$MODEL_IMAGE_NAME" \
    --runtime_envs MODEL_VIDEO_NAME="$MODEL_VIDEO_NAME" \
    --runtime_envs DATABASE_TOS_BUCKET="$DATABASE_TOS_BUCKET" \
    --runtime_envs DATABASE_TOS_REGION="$DATABASE_TOS_REGION" \
    --runtime_envs DATABASE_VIKING_COLLECTION="$DATABASE_VIKING_COLLECTION"
```
Follow the prompts to input application name, entry file (`agent.py`), etc.

### 2. Launch Cloud Service

```bash
agentkit launch
```

### 3. Invoke Test

```bash
agentkit invoke 'Generate a manga about an ancient swordsman in ink wash painting style.'
```

## Future Extensions

1.  **Finer Control**: Add more detailed style parameter controls in the Director Agent.
2.  **Human-in-the-Loop**: Add a manual review step after the Screenwriter generates the script.
3.  **Multimodal Input**: Support user uploads of reference images or novel text as input.

## References

- [VeADK Official Documentation](https://volcengine.github.io/veadk-python/)
- [AgentKit Development Guide](https://volcengine.github.io/agentkit-sdk-python/)

## License

This project is licensed under the Apache 2.0 License.
