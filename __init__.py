import os
now_dir = os.path.dirname(os.path.abspath(__file__))

from huggingface_hub import snapshot_download
if not os.path.isfile(os.path.join(now_dir,"pretrained_models","hallo","net.pth")):
    snapshot_download(repo_id="fudan-generative-ai/hallo",local_dir=os.path.join(now_dir,"pretrained_models"))
else:
    print("Hallo use cache models,make sure your 'pretrained_models' complete")
    
from .nodes import PreViewVideo,HalloNode,LoadImagePath, LoadAudio
WEB_DIRECTORY = "./web"
# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LoadAudio": LoadAudio,
    "PreViewVideo": PreViewVideo,
    "HalloNode": HalloNode,
    "LoadImagePath": LoadImagePath
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "HalloNode": "HalloNode",
    "PreViewVideo": "PreView Video",
    "LoadImagePath": "LoadImagePath",
    "LoadAudio": "AudioLoader"
}
