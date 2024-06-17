# ComfyUI-Hallo
a comfyui custom node for [hallo](https://github.com/fudan-generative-vision/hallo)

<div>
  <figure>
  <img alt='webpage' src="web.png?raw=true" width="600px"/>
  <figure>
</div>

## How to use
make sure `ffmpeg` is worked in your commandline
for Linux
```
apt update
apt install ffmpeg
```
for Windows,you can install `ffmpeg` by [WingetUI](https://github.com/marticliment/WingetUI) automatically

then!
```
## insatll xformers match your torch,for torch==2.1.0+cu121
pip install xformers==0.0.22.post7
pip install accelerate 
# in ComfyUI/custom_nodes
git clone https://github.com/AIFSH/ComfyUI-Hallo.git
cd ComfyUI-Hallo
pip install -r requirements.txt
```
weights will be downloaded from huggingface

## Tutorial
- [Demo](https://b23.tv/SZFuzlK)

## WeChat Group
<div>
  <figure>
  <img alt='Wechat' src="wechat.jpg?raw=true" width="300px"/>
  <figure>
</div>

## Thanks
[hallo](https://github.com/fudan-generative-vision/hallo)
