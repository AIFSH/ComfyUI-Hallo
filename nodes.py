import os,sys
import yaml
import folder_paths

now_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = folder_paths.get_input_directory()
output_dir = folder_paths.get_output_directory()
ckpt_dir = os.path.join(now_dir,"pretrained_weights")

class HalloNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "source_image": ("IMAGE",),
                "driving_audio":("AUDIO",),
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
            }
        }
    RETURN_TYPES = ("VIDEO",)
    #RETURN_NAMES = ("image_output_name",)

    FUNCTION = "generate"

    #OUTPUT_NODE = False

    CATEGORY = "AIFSH_Hallo"

    def generate(self,source_image,driving_audio,pose_weight,face_weight,lip_weight,face_expand_ratio):
        python_exec = sys.executable or "python"
        infer_py = os.path.join(now_dir,"Hallo","scripts","inference.py")
        default_yaml_path = os.path.join(now_dir,"Hallo","configs","inference","default.yaml")
        with open(default_yaml_path, 'r', encoding="utf-8") as f:
            yaml_data = yaml.load(f.read(),Loader=yaml.SafeLoader)
        yaml_data["source_image"] = source_image
        yaml_data['driving_audio'] = driving_audio
        yaml_data['audio_ckpt_dir'] = os.path.join(ckpt_dir,"hallo")
        yaml_data['base_model_path'] = os.path.join(ckpt_dir,"stable-diffusion-v1-5")
        yaml_data['motion_module_path'] = os.path.join(ckpt_dir,"motion_module","mm_sd_v15_v2.ckpt")
        yaml_data['face_analysis']['model_path'] = os.path.join(ckpt_dir,"face_analysis")
        yaml_data['wav2vec']['model_path'] = os.path.join(ckpt_dir,"wav2vec","wav2vec2-base-960h")
        yaml_data['audio_separator']['model_path'] = os.path.join(ckpt_dir,"audio_separator","Kim_Vocal_2.onnx")
        yaml_data['vae']['model_path'] = os.path.join(ckpt_dir,"sd-vae-ft-mse")

        tmp_yaml_path = os.path.join(now_dir,'tmp.yaml')
        with open(tmp_yaml_path,'w', encoding="utf-8") as f:
            yaml.dump(data=yaml_data,stream=f,Dumper=yaml.CDumper)

        outfile = os.path.join(output_dir,f"{}.mp4")
        cmd = f"""{python_exec} {infer_py} --config "{tmp_yaml_path}" -output {outfile} --pose_weight {pose_weight} --face_weight {face_weight} --lip_weight {lip_weight} --face_expand_ratio {face_expand_ratio}"""
        print(cmd)
        os.system(cmd)
        return (outfile, )

class LoadAudio:
    @classmethod
    def INPUT_TYPES(s):
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.split('.')[-1].lower() in ["wav", "mp3","flac","m4a"]]
        return {"required":
                    {"audio": (sorted(files),)},
                }

    CATEGORY = "AIFSH_Hallo"

    RETURN_TYPES = ("AUDIO",)
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

    RETURN_TYPES = ("IMAGE",)
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
