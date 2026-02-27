import os
from typing import List, Dict

# 假设 VikingDB SDK 已经安装，如果未安装，可以暂时模拟
# from vikingdb import VikingDBService 

def search_good_examples(query: str, limit: int = 3) -> str:
    """
    Search for high-quality motion prompt examples from VikingDB based on the user's query.
    
    Args:
        query: The description of the motion or scene (e.g., "sword fighting", "running in rain").
        limit: Number of examples to return.
        
    Returns:
        A string containing the retrieved examples formatted for the agent.
    """
    print(f"[VikingDB] Searching for examples related to: {query}")
    
    # TODO: Replace with actual VikingDB SDK call
    # 
    # service = VikingDBService(host=..., region=..., scheme='http')
    # collection = service.get_collection("motion_prompts")
    # results = collection.search(query_text=query, limit=limit)
    
    # Mock data for demonstration
    mock_database = {
        "running": [
            "Camera tracks side-view of character running, motion blur on background, high shutter speed style.",
            "Dynamic low angle shot of feet splashing in puddles, slow motion droplets, intense action."
        ],
        "fighting": [
            "Fast cuts between sword clashes, sparks flying, cinematic lighting, impact frames.",
            "Over-the-shoulder shot of character drawing weapon, focus shift from hand to enemy."
        ],
        "crying": [
            "Close-up on eyes, tears welling up, subtle facial micro-expressions, soft lighting.",
            "Rain running down face masking tears, melancholic atmosphere, slow zoom out."
        ]
    }
    
    # Simple keyword matching for mock
    found_examples = []
    for key, examples in mock_database.items():
        if key in query.lower():
            found_examples.extend(examples)
            
    if not found_examples:
        # Return generic high-quality examples if no match
        found_examples = [
            "Cinematic pan right, revealing the vast cityscape, volumetric lighting, high detail.",
            "Slow zoom in on character's expression, subtle wind movement in hair, emotional atmosphere."
        ]
    
    # Format output
    result_str = "Found the following high-quality references from VikingDB:\n"
    for i, ex in enumerate(found_examples[:limit]):
        result_str += f"{i+1}. {ex}\n"
        
    return result_str
