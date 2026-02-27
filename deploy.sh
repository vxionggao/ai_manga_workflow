#!/bin/bash

# Load environment variables from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found!"
    exit 1
fi

echo "🚀 Configuring AgentKit deployment..."

# 1. Detailed Configuration
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

echo "✅ Configuration complete."
echo "🚀 Launching Agent to Cloud..."

# 3. Launch
agentkit launch
