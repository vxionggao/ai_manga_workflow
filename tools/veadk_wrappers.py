import os
from typing import Dict, List
from veadk.tools.builtin_tools.image_generate import image_generate as original_image_generate
from veadk.tools.builtin_tools.video_generate import video_generate as original_video_generate
from google.adk.tools import ToolContext
from tools.tos_tools import upload_file_to_tos, file_download

async def image_generate(tasks: list[dict], tool_context, timeout: int = 600) -> Dict:
    """
    Wrapper around veadk's image_generate to ensure images are uploaded to TOS.
    """
    # 1. Call original veadk tool
    result = await original_image_generate(tasks, tool_context, timeout)
    
    # 2. Process results and upload to TOS
    if result.get("status") == "success":
        new_success_list = []
        for item in result.get("success_list", []):
            new_item = {}
            for key, url in item.items():
                # Upload to TOS
                try:
                    print(f"[Wrapper] Uploading image to TOS: {url}")
                    downloaded_paths = file_download([url])
                    if downloaded_paths:
                        local_path = downloaded_paths[0]
                        tos_url = upload_file_to_tos(local_path)
                        if tos_url:
                            print(f"[Wrapper] Upload success: {tos_url}")
                            new_item[key] = tos_url
                            # Update tool context state
                            tool_context.state[f"{key}_url"] = tos_url
                        else:
                            new_item[key] = url
                        # Cleanup
                        if os.path.exists(local_path):
                            os.remove(local_path)
                    else:
                        new_item[key] = url
                except Exception as e:
                    print(f"[Wrapper] Upload failed: {e}")
                    new_item[key] = url
            new_success_list.append(new_item)
        result["success_list"] = new_success_list
        
    return result

async def video_generate(
    params: list,
    tool_context: ToolContext,
    batch_size: int = 10,
    max_wait_seconds: int = 1200,
) -> Dict:
    """
    Wrapper around veadk's video_generate to ensure videos are uploaded to TOS.
    """
    # 0. Patch params to ensure video_name exists
    import uuid
    for i, item in enumerate(params):
        if "video_name" not in item or not item["video_name"]:
            # Auto-generate a video name if missing
            auto_name = f"auto_video_{uuid.uuid4().hex[:8]}.mp4"
            print(f"[Wrapper] Auto-filling missing video_name for task {i}: {auto_name}")
            item["video_name"] = auto_name

    # 1. Call original veadk tool
    result = await original_video_generate(params, tool_context, batch_size, max_wait_seconds)
    
    # 2. Process results and upload to TOS
    if result.get("status") == "success":
        new_success_list = []
        for item in result.get("success_list", []):
            new_item = {}
            for key, url in item.items():
                # Upload to TOS
                try:
                    print(f"[Wrapper] Uploading video to TOS: {url}")
                    downloaded_paths = file_download([url])
                    if downloaded_paths:
                        local_path = downloaded_paths[0]
                        tos_url = upload_file_to_tos(local_path)
                        if tos_url:
                            print(f"[Wrapper] Upload success: {tos_url}")
                            new_item[key] = tos_url
                            # Update tool context state
                            tool_context.state[f"{key}_video_url"] = tos_url
                        else:
                            new_item[key] = url
                        # Cleanup
                        if os.path.exists(local_path):
                            os.remove(local_path)
                    else:
                        new_item[key] = url
                except Exception as e:
                    print(f"[Wrapper] Upload failed: {e}")
                    new_item[key] = url
            new_success_list.append(new_item)
        result["success_list"] = new_success_list
        
    return result
