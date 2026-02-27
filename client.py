import asyncio
import httpx
import requests
import os
from google.adk.cli.adk_web_server import CreateSessionRequest, RunAgentRequest
from google.genai.types import Content, Part

if __name__ == "__main__":
    # Step 0: setup running configs
    app_name = "ai_manga_app"  # Must match app_name in agent.py (if specified in App init) or just be consistent
    # Note: In agent.py we didn't explicitly set app_name in AgentkitAgentServerApp, so it might use agent name or default.
    # However, for the path /apps/{app_name}/..., we need to know what the server expects.
    # AgentkitAgentServerApp usually registers the agent name or a default app name.
    # Let's assume it registers the agent name "manga_workflow_agent" or we can pass app_name to AgentkitAgentServerApp.
    # In my agent.py update, I didn't pass app_name to AgentkitAgentServerApp. 
    # Let's check the reference agent.py again. 
    # Reference agent.py: agent_server_app = AgentkitAgentServerApp(agent=root_agent, ...)
    # Reference client.py: app_name = "pre_process_agent" (which is the name of one of the agents, but root is customer_service_agent).
    # Actually in reference, root_agent = customer_service_agent. 
    # Let's try using the agent name "manga_workflow_agent".
    
    app_name = "manga_workflow_agent" 
    user_id = "demo_user"
    session_id = "client_test_session"
    base_url = "http://127.0.0.1:8000"
    api_key = "agentkit test key" # Default test key

    # Step 1: create a session
    def create_session():
        print(f"Creating session {session_id} for user {user_id}...")
        create_session_request = CreateSessionRequest(
            session_id=session_id,
        )

        # The URL structure is /apps/{app_name}/users/{user_id}/sessions/{session_id}
        url = f"{base_url}/apps/{app_name}/users/{user_id}/sessions/{create_session_request.session_id}"
        
        try:
            response = requests.post(
                url=url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            print(f"[create session] Response from server: {response.json()}")
            return create_session_request.session_id
        except Exception as e:
            print(f"[create session] Failed: {e}")
            if 'response' in locals():
                print(response.text)
            return None

    # Step 2: run agent with SSE
    async def send_request(message: str):
        sid = create_session()
        if not sid:
            return

        print(f"[run agent] Sending message: {message}")
        print("[run agent] Event from server:")

        run_agent_request = RunAgentRequest(
            app_name=app_name,
            user_id=user_id,
            session_id=sid,
            new_message=Content(parts=[Part(text=message)], role="user"),
            stream=True,
        )

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{base_url}/run_sse",
                json=run_agent_request.model_dump(exclude_none=True),
                headers={"Authorization": f"Bearer {api_key}"},
            ) as r:
                async for line in r.aiter_lines():
                    if line:
                        print(line)

    async def main():
        await send_request(
            "Generate a cyberpunk style manga about a courier girl delivering a mysterious package in Neo-Tokyo."
        )

    asyncio.run(main())
