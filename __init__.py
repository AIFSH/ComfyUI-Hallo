import os,site

now_dir = os.path.dirname(os.path.abspath(__file__))
site_packages_roots = []
for path in site.getsitepackages():
    if "packages" in path:
        site_packages_roots.append(path)
if(site_packages_roots==[]):site_packages_roots=["%s/runtime/Lib/site-packages" % now_dir]

for site_packages_root in site_packages_roots:
    if os.path.exists(site_packages_root):
        try:
            with open("%s/Hallo.pth" % (site_packages_root), "w") as f:
                f.write(
                    "%s\n%s/Hallo\n"
                    % (now_dir,now_dir)
                )
            break
        except PermissionError:
            raise PermissionError

if os.path.isfile("%s/Hallo.pth" % (site_packages_root)):
    print("!!!Hallo path was added to " + "%s/Hallo.pth" % (site_packages_root) 
    + "\n if meet No module named 'hallo' error,please restart comfyui")

from huggingface_hub import snapshot_download

if not os.path.isfile(os.path.join(now_dir,"pretrained_models","hallo","net.pth")):
    snapshot_download(repo_id="fudan-generative-ai/hallo",local_dir=os.path.join(now_dir,"pretrained_models"))
else:
    print("Hallo use cache models,make sure your 'pretrained_models' complete")
    
from .nodes import PreViewVideo,HalloNode,LoadImagePath, LoadAudioPath
WEB_DIRECTORY = "./web"
# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LoadAudioPath": LoadAudioPath,
    "PreViewVideo": PreViewVideo,
    "HalloNode": HalloNode,
    "LoadImagePath": LoadImagePath
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "HalloNode": "HalloNode",
    "PreViewVideo": "PreView Video",
    "LoadImagePath": "LoadImagePath",
    "LoadAudio": "LoadAudioPath"
}
