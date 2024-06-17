import { app } from "../../../scripts/app.js";
import { api } from '../../../scripts/api.js'
import { ComfyWidgets } from "../../../scripts/widgets.js"

function fitHeight(node) {
    node.setSize([node.size[0], node.computeSize([node.size[0], node.size[1]])[1]])
    node?.graph?.setDirtyCanvas(true);
}

function previewAudio(node,file){
    while (node.widgets.length > 2){
        node.widgets.pop();
    }
    try {
        var el = document.getElementById("uploadAudio");
        el.remove();
    } catch (error) {
        console.log(error);
    }
    var element = document.createElement("div");
    element.id = "uploadAudio";
    const previewNode = node;
    var previewWidget = node.addDOMWidget("audiopreview", "preview", element, {
        serialize: false,
        hideOnZoom: false,
        getValue() {
            return element.value;
        },
        setValue(v) {
            element.value = v;
        },
    });
    previewWidget.computeSize = function(width) {
        if (this.aspectRatio && !this.parentEl.hidden) {
            let height = (previewNode.size[0]-20)/ this.aspectRatio + 10;
            if (!(height > 0)) {
                height = 0;
            }
            this.computedHeight = height + 10;
            return [width, height];
        }
        return [width, -4];//no loaded src, widget should not display
    }
    // element.style['pointer-events'] = "none"
    previewWidget.value = {hidden: false, paused: false, params: {}}
    previewWidget.parentEl = document.createElement("div");
    previewWidget.parentEl.className = "audio_preview";
    previewWidget.parentEl.style['width'] = "100%"
    element.appendChild(previewWidget.parentEl);
    previewWidget.audioEl = document.createElement("audio");
    previewWidget.audioEl.controls = true;
    previewWidget.audioEl.loop = false;
    previewWidget.audioEl.muted = false;
    previewWidget.audioEl.style['width'] = "100%"
    previewWidget.audioEl.addEventListener("loadedmetadata", () => {

        previewWidget.aspectRatio = previewWidget.audioEl.audioWidth / previewWidget.audioEl.audioHeight;
        fitHeight(this);
    });
    previewWidget.audioEl.addEventListener("error", () => {
        //TODO: consider a way to properly notify the user why a preview isn't shown.
        previewWidget.parentEl.hidden = true;
        fitHeight(this);
    });

    let params =  {
        "filename": file,
        "type": "input",
    }
    
    previewWidget.parentEl.hidden = previewWidget.value.hidden;
    previewWidget.audioEl.autoplay = !previewWidget.value.paused && !previewWidget.value.hidden;
    let target_width = 256
    if (element.style?.width) {
        //overscale to allow scrolling. Endpoint won't return higher than native
        target_width = element.style.width.slice(0,-2)*2;
    }
    if (!params.force_size || params.force_size.includes("?") || params.force_size == "Disabled") {
        params.force_size = target_width+"x?"
    } else {
        let size = params.force_size.split("x")
        let ar = parseInt(size[0])/parseInt(size[1])
        params.force_size = target_width+"x"+(target_width/ar)
    }
    
    previewWidget.audioEl.src = api.apiURL('/view?' + new URLSearchParams(params));

    previewWidget.audioEl.hidden = false;
    previewWidget.parentEl.appendChild(previewWidget.audioEl)
}

function audioUpload(node, inputName, inputData, app) {
    const audioWidget = node.widgets.find((w) => w.name === "audio");
    let uploadWidget;
    /* 
    A method that returns the required style for the html 
    */
    var default_value = audioWidget.value;
    Object.defineProperty(audioWidget, "value", {
        set : function(value) {
            this._real_value = value;
        },

        get : function() {
            let value = "";
            if (this._real_value) {
                value = this._real_value;
            } else {
                return default_value;
            }

            if (value.filename) {
                let real_value = value;
                value = "";
                if (real_value.subfolder) {
                    value = real_value.subfolder + "/";
                }

                value += real_value.filename;

                if(real_value.type && real_value.type !== "input")
                    value += ` [${real_value.type}]`;
            }
            return value;
        }
    });
    async function uploadFile(file, updateNode, pasted = false) {
        try {
            // Wrap file in formdata so it includes filename
            const body = new FormData();
            body.append("image", file);
            if (pasted) body.append("subfolder", "pasted");
            const resp = await api.fetchApi("/upload/image", {
                method: "POST",
                body,
            });

            if (resp.status === 200) {
                const data = await resp.json();
                // Add the file to the dropdown list and update the widget value
                let path = data.name;
                if (data.subfolder) path = data.subfolder + "/" + path;

                if (!audioWidget.options.values.includes(path)) {
                    audioWidget.options.values.push(path);
                }

                if (updateNode) {
                    audioWidget.value = path;
                    previewAudio(node,path)
                    
                }
            } else {
                alert(resp.status + " - " + resp.statusText);
            }
        } catch (error) {
            alert(error);
        }
    }

    const fileInput = document.createElement("input");
    Object.assign(fileInput, {
        type: "file",
        accept: "audio/mp3,audio/wav,audio/flac,audio/m4a",
        style: "display: none",
        onchange: async () => {
            if (fileInput.files.length) {
                await uploadFile(fileInput.files[0], true);
            }
        },
    });
    document.body.append(fileInput);

    // Create the button widget for selecting the files
    uploadWidget = node.addWidget("button", "choose audio file to upload", "Audio", () => {
        fileInput.click();
    });

    uploadWidget.serialize = false;

    previewAudio(node, audioWidget.value);
    const cb = node.callback;
    audioWidget.callback = function () {
        previewAudio(node,audioWidget.value);
        if (cb) {
            return cb.apply(this, arguments);
        }
    };

    return { widget: uploadWidget };
}

ComfyWidgets.AUDIOPLOAD = audioUpload;

app.registerExtension({
	name: "Hallo.UploadAudio",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData?.name == "LoadAudio") {
			nodeData.input.required.upload = ["AUDIOPLOAD"];
		}
	},
});

