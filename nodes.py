import os,sys
import yaml
import time
import argparse
import folder_paths
from Hallo.scripts.inference import inference_process

now_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = folder_paths.get_input_directory()
output_dir = folder_paths.get_output_directory()
ckpt_dir = os.path.join(now_dir,"pretrained_models")
print(ckpt_dir)

class HalloNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "source_image": ("IMAGEPATH",),
                "driving_audio":("AUDIOPATH",),
                "pose_weight" :("FLOAT",{
                    "default": 1.
                }),
                "face_weight":("FLOAT",{
                    "default": 1.
                }),
                "lip_weight":("FLOAT",{
                    "default": 1.
                }),
                "face_expand_ratio":("FLOAT",{
                    "default": 1.2
                })
            },
            "optional":{
                "sd_model": (folder_paths.get_filename_list("diffusers"),),
            }
        }
    RETURN_TYPES = ("VIDEO",)
    #RETURN_NAMES = ("image_output_name",)

    FUNCTION = "generate"

    #OUTPUT_NODE = False

    CATEGORY = "AIFSH_Hallo"

    def generate(self,source_image,driving_audio,pose_weight,face_weight,lip_weight,face_expand_ratio,sd_model=None):
        python_exec = sys.executable or "python"
        infer_py = os.path.join(now_dir,"Hallo","scripts","inference.py")
        default_yaml_path = os.path.join(now_dir,"Hallo","configs","inference","default.yaml")
        with open(default_yaml_path, 'r', encoding="utf-8") as f:
            yaml_data = yaml.load(f.read(),Loader=yaml.SafeLoader)
        # yaml_data["source_image"] = source_image
        # yaml_data['driving_audio'] = driving_audio
        yaml_data['save_path'] = os.path.join(output_dir, "hallo")
        yaml_data['audio_ckpt_dir'] = os.path.join(ckpt_dir,"hallo")
        if sd_model is not None and "safetensors" not in sd_model:
            base_model_path = folder_paths.get_full_path("diffusers", sd_model)
        else:
            base_model_path = os.path.join(ckpt_dir,"stable-diffusion-v1-5")

        yaml_data['base_model_path'] = base_model_path
        print(yaml_data['base_model_path'])
        yaml_data['motion_module_path'] = os.path.join(ckpt_dir,"motion_module","mm_sd_v15_v2.ckpt")
        yaml_data['face_analysis']['model_path'] = os.path.join(ckpt_dir,"face_analysis")
        yaml_data['wav2vec']['model_path'] = os.path.join(ckpt_dir,"wav2vec","wav2vec2-base-960h")
        yaml_data['audio_separator']['model_path'] = os.path.join(ckpt_dir,"audio_separator","Kim_Vocal_2.onnx")
        yaml_data['vae']['model_path'] = os.path.join(ckpt_dir,"sd-vae-ft-mse")

        tmp_yaml_path = os.path.join(now_dir,'tmp.yaml')
        with open(tmp_yaml_path,'w', encoding="utf-8") as f:
            yaml.dump(data=yaml_data,stream=f,Dumper=yaml.Dumper)

        outfile = os.path.join(output_dir,f"hallo_{time.time_ns()}.mp4")
        os.environ["face_landmarker"] = os.path.join(ckpt_dir,"face_analysis","models","face_landmarker_v2_with_blendshapes.task")
        cmd = f"""{python_exec} {infer_py} --config "{tmp_yaml_path}" --source_image "{source_image}" --driving_audio "{driving_audio}" --output {outfile} --pose_weight {pose_weight} --face_weight {face_weight} --lip_weight {lip_weight} --face_expand_ratio {face_expand_ratio}"""
        
        print(cmd)
        os.system(cmd)
        os.remove(tmp_yaml_path)
        return (outfile, )

class LoadAudioPath:
    @classmethod
    def INPUT_TYPES(s):
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.split('.')[-1].lower() in ["wav", "mp3","flac","m4a"]]
        return {"required":
                    {"audio": (sorted(files),)},
                }

    CATEGORY = "AIFSH_Hallo"

    RETURN_TYPES = ("AUDIOPATH",)
    FUNCTION = "load_audio"

    def load_audio(self, audio):
        audio_path = folder_paths.get_annotated_filepath(audio)
        return (audio_path,)

class LoadImagePath:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required":
                    {"image": (sorted(files), {"image_upload": True})},
                }

    CATEGORY = "AIFSH_Hallo"

    RETURN_TYPES = ("IMAGEPATH",)
    FUNCTION = "load_image"
    def load_image(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        return (image_path,)
    
class PreViewVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":{
            "video":("VIDEO",),
        }}
    
    CATEGORY = "AIFSH_Hallo"
    DESCRIPTION = "hello world!"

    RETURN_TYPES = ()

    OUTPUT_NODE = True

    FUNCTION = "load_video"

    def load_video(self, video):
        video_name = os.path.basename(video)
        video_path_name = os.path.basename(os.path.dirname(video))
        return {"ui":{"video":[video_name,video_path_name]}}
