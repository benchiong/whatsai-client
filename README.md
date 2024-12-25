<div align="center">

![logo](https://github.com/user-attachments/assets/0b23e781-d06f-4000-9b63-a5ff429d09a1)

# WhatsAI - An easy-to-use UI fully based on ComfyUI.

[license]: https://img.shields.io/github/license/benchiong/whatsai-client
[release-version]: https://img.shields.io/github/v/tag/benchiong/whatsai-client

[![][license]](https://github.com/benchiong/whatsai-client/blob/main/LICENSE)
[![][release-version]](https://github.com/benchiong/whatsai-client/releases/latest)

</div>

Simply put: You can translate any ComfyUI workflow into a WhatsAI Card (a UI built with React and Mantine).

### WhatsUI Card and ComfyUI Workflow
| WhatsAI Card              |  ComfyUI Workflow |
| ---------------------- |  ----------- |
| Stable Diffusion Image-to-Image|  [ComfyUI Img2Img](https://comfyanonymous.github.io/ComfyUI_examples/img2img/)     |
| Stable-Diffusion-Text-to-Image | [ComfyUI Lora](https://comfyanonymous.github.io/ComfyUI_examples/lora/)  |
| Stable Diffusion Inpaint   | [ComfyUI Inpaint](https://comfyanonymous.github.io/ComfyUI_examples/inpaint/)   |
| Stable Diffusion Outpaint  | [ComfyUI Outpaint](https://comfyanonymous.github.io/ComfyUI_examples/inpaint/#outpainting)    |
| SDXL With Refiner              | [ComfyUI SDXL](https://comfyanonymous.github.io/ComfyUI_examples/sdxl/)    |
| SD3                            | [ComfyUI SD3](https://comfyanonymous.github.io/ComfyUI_examples/sd3/) |
| Flux Dev                       | [ComfyUI Flux Dev](https://comfyanonymous.github.io/ComfyUI_examples/flux/#flux-dev)     |
| Flux Schnell                   | [ComfyUI Flux Schnell](https://comfyanonymous.github.io/ComfyUI_examples/flux/#flux-schnell)  |
| Flux Inpaint    | [ComfyUI Flux Inpaint](https://comfyanonymous.github.io/ComfyUI_examples/flux/#fill-inpainting-model)   |
| Flux Outpaint   | [ComfyUI Flux Outpaint](https://comfyanonymous.github.io/ComfyUI_examples/flux/#fill-inpainting-model)    |
| Lightricks Text-to-Video    | [ComfyUI LTX-T2V](https://comfyanonymous.github.io/ComfyUI_examples/ltxv/#text-to-video)   |
| Lightricks Image-to-Video   | [ComfyUI LTX-I2V](https://comfyanonymous.github.io/ComfyUI_examples/ltxv/#image-to-video)    |

more are coming... 

![cover](https://github.com/user-attachments/assets/73759797-e14a-48ea-9a76-d47c46b6f931)

### Installation

This project consists of an **Electron + Next.js frontend** and a **Python backend**. The `backend-manager` is a utility tool designed to manage the backend during packaging. For now, you can ignore it since the packaging process is still being optimized.

#### Steps to Install

##### Clone the repository

git clone [https://github.com/your-repo-name.git](https://github.com/benchiong/whatsai-client.git)

##### Install the Frontend (Electron + Next.js):

cd frontend

__Install dependencies: Ensure you have Node.js installed.__

```bash
npm install
nextron --renderer-port 6791

This will start the Next.js frontend and Electron in development mode.

```

__Install the Backend (Python):__

Navigate to the backend directory:
```bash
cd backend

# (Optional) Set up a Python virtual environment:
python3 -m venv venv
source venv/bin/activate

# On Windows: venv\Scripts\activate


```
__Install dependencies: Ensure you have Python 3.12 installed.__

```bash

pip install -r requirements.txt
python main.py

```

You can also check out the [ComfyUI](https://github.com/comfyanonymous/ComfyUI) installation guide for reference.


Ensure both the frontend and backend are running simultaneously for the full application to work.

Frontend dependencies are listed in package.json, while backend dependencies are managed via requirements.txt.
If you encounter issues, verify that your Node.js and Python versions meet the requirements.


## Credits
- ComfyUI - https://github.com/comfyanonymous/ComfyUI
- CivitAI - https://github.com/civitai/civitai
- WebUI   - https://github.com/AUTOMATIC1111/stable-diffusion-webui
- Fooocus - https://github.com/lllyasviel/Fooocus
- ComfyBox - https://github.com/space-nuko/ComfyBox
- CivitAI Helper - https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper
- Stable Diffusion webui Infinite Image Browsing - https://github.com/zanllp/sd-webui-infinite-image-browsing

