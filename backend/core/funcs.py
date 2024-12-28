import base64
import io
import enum
import json
import math
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageSequence, ImageOps
from PIL.PngImagePlugin import PngInfo
from torch import Tensor

import comfy.sd
import comfy.model_management
import comfy.samplers
import comfy.sample
import comfy.utils
import comfy.model_patcher
import comfy.controlnet
from comfy.taesd.taesd import TAESD
from core.abstracts.func import Func, IOInfo
from data_type.whatsai_artwork import Artwork
from data_type.whatsai_model_dir import ModelDir
from data_type.whatsai_model_info import ModelInfo
from core.extras import tae_model_info_list
from misc.helpers import pillow, get_meta_info, conditioning_set_values
from misc.logger import logger

try:
    from spandrel_extra_arches import EXTRA_REGISTRY
    from spandrel import MAIN_REGISTRY, ModelLoader, ImageModelDescriptor

    MAIN_REGISTRY.add(*EXTRA_REGISTRY)
    logger.info("Successfully imported spandrel_extra_arches.")
except Exception as e:
    logger.debug("Fail to imported spandrel_extra_arches: {}".format(e))


class Func_CheckpointLoaderSimple(Func):
    def __init__(self, name="Checkpoint Loader"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='checkpoint_id', data_type='STRING')
        )

        self.set_outputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='clip', data_type='CLIP'),
            IOInfo(name='vae', data_type='VAE'),
        )

    def run(self, checkpoint_id):
        checkpoint_path = ModelInfo.get(checkpoint_id).local_path
        embedding_directories = ModelDir.get_dirs('embedding')

        out = comfy.sd.load_checkpoint_guess_config(
            checkpoint_path,
            output_vae=True,
            output_clip=True,
            embedding_directory=embedding_directories
        )

        return out[:3]


class Func_VAELoader(Func):
    def __init__(self, name="Load VAE"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='vae_id', data_type='STRING')
        )

        self.set_outputs(
            IOInfo(name='vae', data_type='VAE'),
        )

    def run(self, vae_id):
        vae_model_info = ModelInfo.get(vae_id)

        tae_model_infos = tae_model_info_list()
        is_vae_model_tae = False

        for tae_model in tae_model_infos:
            if tae_model.local_path == vae_model_info.local_path:
                is_vae_model_tae = True
                break

        if is_vae_model_tae:
            sd = self.load_taesd(vae_model_info)
        else:
            vae_path = vae_model_info.local_path
            sd = comfy.utils.load_torch_file(vae_path)

        vae = comfy.sd.VAE(sd=sd)
        return (vae,)

    def load_taesd(self, vae_model):
        encoder_path, decoder_path = vae_model.local_path.split('|')
        name = Path(encoder_path).stem.replace('_encoder', '')
        sd = {}
        enc = comfy.utils.load_torch_file(encoder_path)
        for k in enc:
            sd["taesd_encoder.{}".format(k)] = enc[k]

        dec = comfy.utils.load_torch_file(decoder_path)
        for k in dec:
            sd["taesd_decoder.{}".format(k)] = dec[k]

        if name == "taesd":
            sd["vae_scale"] = torch.tensor(0.18215)
            sd["vae_shift"] = torch.tensor(0.0)
        elif name == "taesdxl":
            sd["vae_scale"] = torch.tensor(0.13025)
            sd["vae_shift"] = torch.tensor(0.0)
        elif name == "taesd3":
            sd["vae_scale"] = torch.tensor(1.5305)
            sd["vae_shift"] = torch.tensor(0.0609)
        elif name == "taef1":
            sd["vae_scale"] = torch.tensor(0.3611)
            sd["vae_shift"] = torch.tensor(0.1159)
        return sd


class Func_CLIPTextEncode(Func):
    def __init__(self, name="ClipTextEncoder"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='clip', data_type='CLIP'),
            IOInfo(name='text', data_type='STRING')

        )

        self.set_outputs(
            IOInfo(name='cond', data_type='CONDITIONING'),
        )

    def run(self, clip, text):
        tokens = clip.tokenize(text)
        output = clip.encode_from_tokens(tokens, return_pooled=True, return_dict=True)
        cond = output.pop("cond")
        return ([[cond, output]],)


class Func_EmptyLatentImage(Func):
    def __init__(self, name='EmptyLatentImage'):
        super().__init__(name=name)

        self.device = comfy.model_management.intermediate_device()

        self.set_inputs(
            IOInfo(name='width', data_type='INT'),
            IOInfo(name='height', data_type='INT')

        )

        self.set_outputs(
            IOInfo(name='latent', data_type='LATENT'),
        )

    def run(self, width, height, batch_size=1):
        latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        return ({"samples": latent},)


def common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=1.0,
                    disable_noise=False, start_step=None, last_step=None, force_full_denoise=False, callback=None):
    latent_image = latent["samples"]
    latent_image = comfy.sample.fix_empty_latent_channels(model, latent_image)

    if disable_noise:
        noise = torch.zeros(latent_image.size(), dtype=latent_image.dtype, layout=latent_image.layout, device="cpu")
    else:
        batch_inds = latent["batch_index"] if "batch_index" in latent else None
        noise = comfy.sample.prepare_noise(latent_image, seed, batch_inds)

    noise_mask = None
    if "noise_mask" in latent:
        noise_mask = latent["noise_mask"]

    disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
    samples = comfy.sample.sample(model, noise, steps, cfg, sampler_name, scheduler, positive, negative, latent_image,
                                  denoise=denoise, disable_noise=disable_noise, start_step=start_step,
                                  last_step=last_step,
                                  force_full_denoise=force_full_denoise, noise_mask=noise_mask, callback=callback,
                                  disable_pbar=disable_pbar, seed=seed)
    out = latent.copy()
    out["samples"] = samples
    return (out,)


class LatentPreviewMethod(enum.Enum):
    Auto = "auto"  # this will use taesd first.
    Latent2RGB = "latent2rgb"
    TAESD = "taesd"


MAX_PREVIEW_RESOLUTION = 512


def preview_to_base64(latent_image):
    latents_ubyte = (((latent_image + 1.0) / 2.0).clamp(0, 1)  # change scale from -1..1 to 0..1
                     .mul(0xFF)  # to 0..255
                     ).to(device="cpu", dtype=torch.uint8,
                          non_blocking=comfy.model_management.device_supports_non_blocking(latent_image.device))

    image = Image.fromarray(latents_ubyte.numpy())
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_byte = buffered.getvalue()
    return 'data:image/png;base64,' + base64.b64encode(img_byte).decode('utf-8')


class LatentPreviewer:
    def decode_latent_to_preview_base64(self, x0):
        pass


class TAESDPreviewerImpl(LatentPreviewer):
    def __init__(self, taesd):
        self.taesd = taesd

    def decode_latent_to_preview_base64(self, x0):
        x_sample = self.taesd.decode(x0[:1])[0].movedim(0, 2)
        return preview_to_base64(x_sample)


class Latent2RGBPreviewer(LatentPreviewer):
    def __init__(self, latent_rgb_factors, latent_rgb_factors_bias=None):
        # self.latent_rgb_factors = torch.tensor(latent_rgb_factors, device="cpu")
        self.latent_rgb_factors = torch.tensor(latent_rgb_factors, device="cpu").transpose(0, 1)
        self.latent_rgb_factors_bias = None
        if latent_rgb_factors_bias is not None:
            self.latent_rgb_factors_bias = torch.tensor(latent_rgb_factors_bias, device="cpu")

    def decode_latent_to_preview_base64(self, x0):
        # self.latent_rgb_factors = self.latent_rgb_factors.to(dtype=x0.dtype, device=x0.device)
        # latent_image = x0[0].permute(1, 2, 0) @ self.latent_rgb_factors
        # return preview_to_base64(latent_image)

        self.latent_rgb_factors = self.latent_rgb_factors.to(dtype=x0.dtype, device=x0.device)
        if self.latent_rgb_factors_bias is not None:
            self.latent_rgb_factors_bias = self.latent_rgb_factors_bias.to(dtype=x0.dtype, device=x0.device)

        if x0.ndim == 5:
            x0 = x0[0, :, 0]
        else:
            x0 = x0[0]

        latent_image = torch.nn.functional.linear(x0.movedim(0, -1), self.latent_rgb_factors,
                                                  bias=self.latent_rgb_factors_bias)
        return preview_to_base64(latent_image)


def get_previewer(preview_method, device, latent_format):
    previewer = None
    if latent_format.taesd_decoder_name is not None and not preview_method == LatentPreviewMethod.Latent2RGB:
        tae_model_infos = ModelInfo.get_taesd_model_infos()
        tae_file_record = None
        for tae_model_file in tae_model_infos:
            if tae_model_file.file_name.startswith(latent_format.taesd_decoder_name):
                tae_file_record = tae_model_file
                break
        if tae_file_record:
            tae_file_path = tae_file_record.local_path
            taesd = TAESD(None, tae_file_path, latent_channels=latent_format.latent_channels).to(device)
            previewer = TAESDPreviewerImpl(taesd)
    else:
        previewer = Latent2RGBPreviewer(latent_format.latent_rgb_factors)
    return previewer


class Func_KSampler(Func):
    def __init__(self,
                 name='kSample',
                 preview_method=LatentPreviewMethod.Auto,
                 preview_steps=3
                 ):
        super().__init__(name=name)
        self.preview_method = preview_method
        self.previewer = None
        self.preview_steps = preview_steps
        self.callback = None

        self.set_inputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
            IOInfo(name='latent_image', data_type='LATENT'),

            IOInfo(name='seed', data_type='INT'),
            IOInfo(name='steps', data_type='INT'),
            IOInfo(name='cfg', data_type='INT'),
            IOInfo(name='sampler_name', data_type='STRING'),
            IOInfo(name='scheduler', data_type='STRING'),
            IOInfo(name='denoise', data_type='FLOAT'),
        )

        self.set_outputs(
            IOInfo(name='latent', data_type='LATENT'),
        )

    def set_callback(self, cb):
        self.callback = cb

    def get_callback(self):
        if not self.callback:
            return None

        def _callback(step, x0, x, total_steps):
            """ Return step, total_steps, and preview_bytes. """
            step += 1
            if step == 1 or step == total_steps or step % self.preview_steps == 0:
                preview_bytes = self.previewer.decode_latent_to_preview_base64(x0)
                self.callback(step, total_steps, preview_bytes)

        return _callback

    def run(self,
            model,
            seed,
            steps,
            cfg,
            sampler_name,
            scheduler,
            positive,
            negative,
            latent_image,
            denoise=1.0,
            ):

        if not self.previewer:
            self.previewer = get_previewer(self.preview_method, model.load_device, model.model.latent_format)

        return common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image,
                               denoise=denoise, callback=self.get_callback())


class Func_KSamplerAdvanced(Func):
    def __init__(self,
                 name='KSamplerAdvanced',
                 preview_method=LatentPreviewMethod.Auto,
                 preview_steps=3
                 ):
        super().__init__(name=name)
        self.preview_method = preview_method
        self.previewer = None
        self.preview_steps = preview_steps

        self.set_inputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='add_noise', data_type='STRING'),
            IOInfo(name='noise_seed', data_type='INT'),
            IOInfo(name='steps', data_type='INT'),
            IOInfo(name='cfg', data_type='INT'),
            IOInfo(name='sampler_name', data_type='STRING'),
            IOInfo(name='scheduler', data_type='STRING'),
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
            IOInfo(name='latent_image', data_type='LATENT'),
            IOInfo(name='start_at_step', data_type='INT'),
            IOInfo(name='end_at_step', data_type='INT'),
            IOInfo(name='return_with_leftover_noise', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='latent', data_type='LATENT'),
        )

    def set_callback(self, cb):
        self.callback = cb

    def get_callback(self):
        if not self.callback:
            return None

        def _callback(step, x0, x, total_steps):
            """ Return step, total_steps, and preview_bytes. """
            step += 1
            if step == 1 or step == total_steps or step % self.preview_steps == 0:
                preview_bytes = self.previewer.decode_latent_to_preview_base64(x0)
                self.callback(step, total_steps, preview_bytes)

        return _callback

    def run(self, model, add_noise, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative,
            latent_image, start_at_step, end_at_step, return_with_leftover_noise, denoise=1.0, callback=None):

        if not self.previewer:
            self.previewer = get_previewer(self.preview_method, model.load_device, model.model.latent_format)

        def _callback(step, x0, x, total_steps):
            step += 1
            if step == 1 or step == total_steps or step % self.preview_steps == 0:
                preview_bytes = self.previewer.decode_latent_to_preview_base64(x0)
                if callback:
                    callback(step, total_steps, preview_bytes)

        force_full_denoise = True
        if return_with_leftover_noise == "enable":
            force_full_denoise = False
        disable_noise = False
        if add_noise == "disable":
            disable_noise = True
        return common_ksampler(model, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image,
                               denoise=denoise, disable_noise=disable_noise, start_step=start_at_step,
                               last_step=end_at_step, force_full_denoise=force_full_denoise,
                               callback=self.get_callback())


class Func_VAEDecode(Func):
    def __init__(self, name="Vae Decode"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='samples', data_type='LATENT'),
            IOInfo(name='vae', data_type='VAE'),
        )

        self.set_outputs(
            IOInfo(name='image', data_type='IMAGE'),
        )

    def run(self, vae, samples):
        images = vae.decode(samples["samples"])
        if len(images.shape) == 5:  # Combine batches
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])
        return (images,)


class Func_VAEEncode(Func):
    def __init__(self, name="Vae Encode"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='pixels', data_type='IMAGE'),
            IOInfo(name='vae', data_type='VAE'),
        )

        self.set_outputs(
            IOInfo(name='latent', data_type='LATENT'),
        )

    def run(self, pixels, vae):
        t = vae.encode(pixels[:, :, :, :3])
        return ({"samples": t},)


class Func_SaveImage(Func):
    def __init__(self, name="Save Image"):
        super().__init__(name=name)

        self.compress_level = 4

        self.set_inputs(
            IOInfo(name='images', data_type='IMAGE'),
        )

        self.set_outputs(
            IOInfo(name='result', data_type='RESULT'),
        )

    def run(self,
            images: Tensor,
            ):
        results = list()
        assert self.prompt, "Prompt must be set where func registered."

        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            metadata = PngInfo()
            metadata.add_text("prompt", json.dumps(self.prompt.model_dump()))

            file_path = Artwork.create_file_path(media_type='image')
            img.save(file_path, pnginfo=metadata, compress_level=self.compress_level)

            meta_info = get_meta_info(file_path)

            artwork = Artwork.add_art_work(
                file_path=file_path,
                card_name=self.prompt.card_name,
                media_type='image',
                meta_info=meta_info,
                prompt=self.prompt,
            )
            results.append(artwork)

        return ({"images": results},)


class Func_CLIPSetLastLayer(Func):
    def __init__(self, name="Clip Skip"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='clip', data_type='CLIP'),
            IOInfo(name='clip_skip', data_type='INT'),
        )

        self.set_outputs(
            IOInfo(name='clip', data_type='CLIP'),
        )

    def run(self, clip, clip_skip):
        clip = clip.clone()
        clip.clip_layer(clip_skip)
        return (clip,)


class Func_LoraLoader(Func):
    def __init__(self, name="LoRA Loader"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='clip', data_type='CLIP'),
            IOInfo(name='lora_id', data_type='STRING'),
            IOInfo(name='weight', data_type='FLOAT'),
        )

        self.set_outputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='clip', data_type='CLIP'),
        )

    def run(self, model, clip, lora_id, weight):
        if weight == 0:
            return model, clip

        lora_path = ModelInfo.get(lora_id).local_path

        # todo: support cache management for this func inner logic.
        lora = comfy.utils.load_torch_file(lora_path, safe_load=True)

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, weight, weight)
        return model_lora, clip_lora


class Func_UpscaleModelLoader(Func):
    def __init__(self, name="Load Upscale Model"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='upscale_model_id', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='upscale_model', data_type='UPSCALE_MODEL'),
        )

    def run(self, upscale_model_id):
        model_path = ModelInfo.get(upscale_model_id).local_path

        sd = comfy.utils.load_torch_file(model_path, safe_load=True)
        if "module.layers.0.residual_group.blocks.0.norm1.weight" in sd:
            sd = comfy.utils.state_dict_prefix_replace(sd, {"module.": ""})
        out = ModelLoader().load_from_state_dict(sd).eval()

        if not isinstance(out, ImageModelDescriptor):
            raise Exception("Upscale model must be a single-image model.")

        return (out,)


class Func_ImageUpscaleWithModel(Func):
    def __init__(self, name="Upscale Image (using Model)"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='upscale_model', data_type='UPSCALE_MODEL'),
            IOInfo(name='image', data_type='IMAGE'),
        )

        self.set_outputs(
            IOInfo(name='image', data_type='IMAGE'),
        )

    def run(self, upscale_model, image):
        device = comfy.model_management.get_torch_device()

        memory_required = comfy.model_management.module_size(upscale_model.model)
        memory_required += (512 * 512 * 3) * image.element_size() * max(upscale_model.scale,
                                                                        1.0) * 384.0  # The 384.0 is an estimate of how much some of these models take, TODO: make it more accurate
        memory_required += image.nelement() * image.element_size()
        comfy.model_management.free_memory(memory_required, device)

        upscale_model.to(device)
        in_img = image.movedim(-1, -3).to(device)

        tile = 512
        overlap = 32

        oom = True
        while oom:
            try:
                steps = in_img.shape[0] * comfy.utils.get_tiled_scale_steps(in_img.shape[3], in_img.shape[2],
                                                                            tile_x=tile, tile_y=tile, overlap=overlap)
                pbar = comfy.utils.ProgressBar(steps)
                s = comfy.utils.tiled_scale(in_img, lambda a: upscale_model(a), tile_x=tile, tile_y=tile,
                                            overlap=overlap, upscale_amount=upscale_model.scale, pbar=pbar)
                oom = False
            except comfy.model_management.OOM_EXCEPTION as e:
                tile //= 2
                if tile < 128:
                    raise e

        upscale_model.to("cpu")
        s = torch.clamp(s.movedim(-3, -1), min=0, max=1.0)
        return (s,)


class Func_LatentScale(Func):
    def __init__(self, name="Upscale Latent"):
        super().__init__(name=name, )

    def run(self, samples, upscale_method, width, height, crop):
        if width == 0 and height == 0:
            s = samples
        else:
            s = samples.copy()

            if width == 0:
                height = max(64, height)
                width = max(64, round(samples["samples"].shape[3] * height / samples["samples"].shape[2]))
            elif height == 0:
                width = max(64, width)
                height = max(64, round(samples["samples"].shape[2] * width / samples["samples"].shape[3]))
            else:
                width = max(64, width)
                height = max(64, height)

            s["samples"] = comfy.utils.common_upscale(samples["samples"], width // 8, height // 8, upscale_method, crop)
        return (s,)


class Func_LoadImage(Func):
    def __init__(self, name="Load Image"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='image_path', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='image', data_type='IMAGE'),
            IOInfo(name='mask', data_type='MASK'),
        )

    def run(self, image_path: str):
        img = pillow(Image.open, image_path)

        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']

        for i in ImageSequence.Iterator(img):
            i = pillow(ImageOps.exif_transpose, i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]

            if image.size[0] != w or image.size[1] != h:
                continue

            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return output_image, output_mask


class Func_HypernetLoader(Func):
    def __init__(self, name="Hypernet Loader"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='hypernet_id', data_type='STRING'),
            IOInfo(name='strength', data_type='FLOAT'),
        )

        self.set_outputs(
            IOInfo(name='model', data_type='MODEL'),
        )

    def run(self, model, hypernet_id, strength):
        hypernet_path = ModelInfo.get(hypernet_id).local_path
        model_hypernet = model.clone()
        patch = self.load_hypernetwork_patch(hypernet_path, strength)
        if patch is not None:
            model_hypernet.set_model_attn1_patch(patch)
            model_hypernet.set_model_attn2_patch(patch)
        return (model_hypernet,)

    def load_hypernetwork_patch(self, path, strength):
        sd = comfy.utils.load_torch_file(path, safe_load=True)
        activation_func = sd.get('activation_func', 'linear')
        is_layer_norm = sd.get('is_layer_norm', False)
        use_dropout = sd.get('use_dropout', False)
        activate_output = sd.get('activate_output', False)
        last_layer_dropout = sd.get('last_layer_dropout', False)

        valid_activation = {
            "linear": torch.nn.Identity,
            "relu": torch.nn.ReLU,
            "leakyrelu": torch.nn.LeakyReLU,
            "elu": torch.nn.ELU,
            "swish": torch.nn.Hardswish,
            "tanh": torch.nn.Tanh,
            "sigmoid": torch.nn.Sigmoid,
            "softsign": torch.nn.Softsign,
            "mish": torch.nn.Mish,
        }

        if activation_func not in valid_activation:
            logger.error(
                "Unsupported Hypernetwork format, if you report it I might implement it. {}   {} {} {} {} {}".format(
                    path, activation_func, is_layer_norm, use_dropout, activate_output, last_layer_dropout))
            return None

        out = {}

        for d in sd:
            try:
                dim = int(d)
            except:
                continue

            output = []
            for index in [0, 1]:
                attn_weights = sd[dim][index]
                keys = attn_weights.keys()

                linears = filter(lambda a: a.endswith(".weight"), keys)
                linears = list(map(lambda a: a[:-len(".weight")], linears))
                layers = []

                i = 0
                while i < len(linears):
                    lin_name = linears[i]
                    last_layer = (i == (len(linears) - 1))
                    penultimate_layer = (i == (len(linears) - 2))

                    lin_weight = attn_weights['{}.weight'.format(lin_name)]
                    lin_bias = attn_weights['{}.bias'.format(lin_name)]
                    layer = torch.nn.Linear(lin_weight.shape[1], lin_weight.shape[0])
                    layer.load_state_dict({"weight": lin_weight, "bias": lin_bias})
                    layers.append(layer)
                    if activation_func != "linear":
                        if (not last_layer) or (activate_output):
                            layers.append(valid_activation[activation_func]())
                    if is_layer_norm:
                        i += 1
                        ln_name = linears[i]
                        ln_weight = attn_weights['{}.weight'.format(ln_name)]
                        ln_bias = attn_weights['{}.bias'.format(ln_name)]
                        ln = torch.nn.LayerNorm(ln_weight.shape[0])
                        ln.load_state_dict({"weight": ln_weight, "bias": ln_bias})
                        layers.append(ln)
                    if use_dropout:
                        if (not last_layer) and (not penultimate_layer or last_layer_dropout):
                            layers.append(torch.nn.Dropout(p=0.3))
                    i += 1

                output.append(torch.nn.Sequential(*layers))
            out[dim] = torch.nn.ModuleList(output)

        class hypernetwork_patch:
            def __init__(self, hypernet, strength):
                self.hypernet = hypernet
                self.strength = strength

            def __call__(self, q, k, v, extra_options):
                dim = k.shape[-1]
                if dim in self.hypernet:
                    hn = self.hypernet[dim]
                    k = k + hn[0](k) * self.strength
                    v = v + hn[1](v) * self.strength

                return q, k, v

            def to(self, device):
                for d in self.hypernet.keys():
                    self.hypernet[d] = self.hypernet[d].to(device)
                return self

        return hypernetwork_patch(out, strength)


class Func_VAEEncodeForInpaint(Func):
    def __init__(self, name="Vae Encode For Inpainting"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='pixels', data_type='IMAGE'),
            IOInfo(name='vae', data_type='VAE'),
            IOInfo(name='mask', data_type='MASK'),
            IOInfo(name='grow_mask_by', data_type='INT'),
        )

        self.set_outputs(
            IOInfo(name='latent', data_type='LATENT'),
        )

    def run(self, vae, pixels, mask, grow_mask_by=6):
        x = (pixels.shape[1] // vae.downscale_ratio) * vae.downscale_ratio
        y = (pixels.shape[2] // vae.downscale_ratio) * vae.downscale_ratio
        mask = torch.nn.functional.interpolate(mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])),
                                               size=(pixels.shape[1], pixels.shape[2]), mode="bilinear")

        pixels = pixels.clone()
        if pixels.shape[1] != x or pixels.shape[2] != y:
            x_offset = (pixels.shape[1] % vae.downscale_ratio) // 2
            y_offset = (pixels.shape[2] % vae.downscale_ratio) // 2
            pixels = pixels[:, x_offset:x + x_offset, y_offset:y + y_offset, :]
            mask = mask[:, :, x_offset:x + x_offset, y_offset:y + y_offset]

        # grow mask by a few pixels to keep things seamless in latent space
        if grow_mask_by == 0:
            mask_erosion = mask
        else:
            kernel_tensor = torch.ones((1, 1, grow_mask_by, grow_mask_by))
            padding = math.ceil((grow_mask_by - 1) / 2)

            mask_erosion = torch.clamp(torch.nn.functional.conv2d(mask.round(), kernel_tensor, padding=padding), 0, 1)

        m = (1.0 - mask.round()).squeeze(1)
        for i in range(3):
            pixels[:, :, :, i] -= 0.5
            pixels[:, :, :, i] *= m
            pixels[:, :, :, i] += 0.5
        t = vae.encode(pixels)

        return ({"samples": t, "noise_mask": (mask_erosion[:, :, :x, :y].round())},)


class Func_ImagePadForOutpaint(Func):
    def __init__(self, name="Image Pad For Outpainting"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='image', data_type='IMAGE'),
            IOInfo(name='left', data_type='INT'),
            IOInfo(name='top', data_type='INT'),
            IOInfo(name='right', data_type='INT'),
            IOInfo(name='bottom', data_type='INT'),
            IOInfo(name='feathering', data_type='INT'),

        )

        self.set_outputs(
            IOInfo(name='image', data_type='IMAGE'),
            IOInfo(name='mask', data_type='MASK'),
        )

    def run(self, image, left, top, right, bottom, feathering):
        d1, d2, d3, d4 = image.size()

        new_image = torch.ones(
            (d1, d2 + top + bottom, d3 + left + right, d4),
            dtype=torch.float32,
        ) * 0.5

        new_image[:, top:top + d2, left:left + d3, :] = image

        mask = torch.ones(
            (d2 + top + bottom, d3 + left + right),
            dtype=torch.float32,
        )

        t = torch.zeros(
            (d2, d3),
            dtype=torch.float32
        )

        if feathering > 0 and feathering * 2 < d2 and feathering * 2 < d3:

            for i in range(d2):
                for j in range(d3):
                    dt = i if top != 0 else d2
                    db = d2 - i if bottom != 0 else d2

                    dl = j if left != 0 else d3
                    dr = d3 - j if right != 0 else d3

                    d = min(dt, db, dl, dr)

                    if d >= feathering:
                        continue

                    v = (feathering - d) / feathering

                    t[i, j] = v * v

        mask[top:top + d2, left:left + d3] = t

        return new_image, mask


class Func_ControlNetLoader(Func):
    def __init__(self, name="ControlNet Loader"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='controlnet_id', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='control_net', data_type='CONTROL_NET'),
        )

    def run(self, controlnet_id):
        controlnet_path = ModelInfo.get(controlnet_id).local_path
        controlnet = comfy.controlnet.load_controlnet(controlnet_path)
        return (controlnet,)


class Func_ControlNetApply(Func):
    def __init__(self, name="Apply ControlNet"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='conditioning', data_type='CONDITIONING'),
            IOInfo(name='control_net', data_type='CONTROL_NET'),
            IOInfo(name='image', data_type='IMAGE'),
            IOInfo(name='strength', data_type='FLOAT'),
        )

        self.set_outputs(
            IOInfo(name='cond', data_type='CONDITIONING'),
        )

    def run(self, conditioning, control_net, image, strength):
        if strength == 0:
            return conditioning

        c = []
        control_hint = image.movedim(-1, 1)
        for t in conditioning:
            n = [t[0], t[1].copy()]
            c_net = control_net.copy().set_cond_hint(control_hint, strength)
            if 'control' in t[1]:
                c_net.set_previous_controlnet(t[1]['control'])
            n[1]['control'] = c_net
            n[1]['control_apply_to_uncond'] = True
            c.append(n)
        return (c,)


class Func_ClipLoader(Func):
    def __init__(self, name="CLIP Loader"):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='clip_id', data_type='STRING'),
            IOInfo(name='type', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='clip', data_type='CLIP'),
        )

    def run(self, clip_id, type="stable_diffusion"):
        clip_path = ModelInfo.get(clip_id).local_path
        embedding_directories = ModelDir.get_dirs('embedding')

        if type == "stable_cascade":
            clip_type = comfy.sd.CLIPType.STABLE_CASCADE
        elif type == "sd3":
            clip_type = comfy.sd.CLIPType.SD3
        elif type == "stable_audio":
            clip_type = comfy.sd.CLIPType.STABLE_AUDIO
        elif type == "mochi":
            clip_type = comfy.sd.CLIPType.MOCHI
        elif type == "ltxv":
            clip_type = comfy.sd.CLIPType.LTXV
        else:
            clip_type = comfy.sd.CLIPType.STABLE_DIFFUSION

        clip = comfy.sd.load_clip(ckpt_paths=[clip_path],
                                  embedding_directory=embedding_directories, clip_type=clip_type)
        return (clip,)


class Func_DualCLIPLoader(Func):
    def __init__(self, name="Dual CLIP Loader"):
        super().__init__(name=name)
        self.set_inputs(
            IOInfo(name='clip_id1', data_type='STRING'),
            IOInfo(name='clip_id2', data_type='STRING'),
            IOInfo(name='type', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='clip', data_type='CLIP'),
        )

    def run(self, clip_id1, clip_id2, type):

        clip_path1 = ModelInfo.get(clip_id1).local_path
        clip_path2 = ModelInfo.get(clip_id2).local_path
        embedding_directories = ModelDir.get_dirs('embedding')

        if type == "sdxl":
            clip_type = comfy.sd.CLIPType.STABLE_DIFFUSION
        elif type == "sd3":
            clip_type = comfy.sd.CLIPType.SD3
        elif type == "flux":
            clip_type = comfy.sd.CLIPType.FLUX

        clip = comfy.sd.load_clip(ckpt_paths=[clip_path1, clip_path2],
                                  embedding_directory=embedding_directories, clip_type=clip_type)
        return (clip,)


class Func_TripleCLIPLoader(Func):
    def __init__(self, name='Triple CLIP Loader'):
        super().__init__(name=name)
        self.set_inputs(
            IOInfo(name='clip_id1', data_type='STRING'),
            IOInfo(name='clip_id2', data_type='STRING'),
            IOInfo(name='clip_id3', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='clip', data_type='CLIP'),
        )

    def run(self, clip_id1, clip_id2, clip_id3):
        clip_path1 = ModelInfo.get(clip_id1).local_path
        clip_path2 = ModelInfo.get(clip_id2).local_path
        clip_path3 = ModelInfo.get(clip_id3).local_path
        embedding_directories = ModelDir.get_dirs('embedding')

        clip = comfy.sd.load_clip(ckpt_paths=[clip_path1, clip_path2, clip_path3],
                                  embedding_directory=embedding_directories)
        return (clip,)


class Func_UNETLoader(Func):
    def __init__(self, name='UNET Loader'):
        super().__init__(name=name)
        self.set_inputs(
            IOInfo(name='unet_id', data_type='STRING'),
            IOInfo(name='weight_dtype', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='model', data_type='MODEL'),
        )

    def run(self, unet_id, weight_dtype):
        unet_path = ModelInfo.get(unet_id).local_path
        model_options = {}
        if weight_dtype == "fp8_e4m3fn":
            model_options["dtype"] = torch.float8_e4m3fn
        elif weight_dtype == "fp8_e5m2":
            model_options["dtype"] = torch.float8_e5m2

        model = comfy.sd.load_diffusion_model(unet_path, model_options=model_options)
        return (model,)


class Func_FluxGuidance(Func):
    def __init__(self, name='FluxGuidance'):
        super().__init__(name=name)
        self.set_inputs(
            IOInfo(name='conditioning', data_type='CONDITIONING'),
            IOInfo(name='guidance', data_type='FLOAT'),
        )

        self.set_outputs(
            IOInfo(name='cond', data_type='CONDITIONING'),
        )

    def run(self, conditioning, guidance):
        c = conditioning_set_values(conditioning, {"guidance": guidance})
        return (c,)


class Func_SamplerCustomAdvanced(Func):
    def __init__(self, name="SamplerCustomAdvanced", preview_method=LatentPreviewMethod.Auto,
                 preview_steps=3):
        super().__init__(name)

        self.preview_method = preview_method
        self.previewer = None
        self.preview_steps = preview_steps
        self.callback = None
        self.x0_output_dict = {}

        self.set_inputs(
            IOInfo(name='noise', data_type='NOISE'),
            IOInfo(name='guider', data_type='GUIDER'),
            IOInfo(name='sampler', data_type='SAMPLER'),
            IOInfo(name='sigmas', data_type='SIGMAS'),
            IOInfo(name='latent_image', data_type='LATENT'),
        )

        self.set_outputs(
            IOInfo(name='output', data_type='LATENT'),
            IOInfo(name='denoised_output', data_type='LATENT'),
        )

    def set_callback(self, cb):
        self.callback = cb

    def get_callback(self):
        if not self.callback:
            return None

        def _callback(step, x0, x, total_steps):
            """ Return step, total_steps, and preview_bytes. """

            self.x0_output_dict["x0"] = x0

            step += 1
            if step == 1 or step == total_steps or step % self.preview_steps == 0:
                preview_bytes = self.previewer.decode_latent_to_preview_base64(x0)
                self.callback(step, total_steps, preview_bytes)

        return _callback

    def run(self, noise, guider, sampler, sigmas, latent_image):
        if not self.previewer:
            self.previewer = get_previewer(
                self.preview_method,
                guider.model_patcher.load_device,
                guider.model_patcher.model.latent_format
            )

        latent = latent_image
        latent_image = latent["samples"]
        latent = latent.copy()
        latent_image = comfy.sample.fix_empty_latent_channels(guider.model_patcher, latent_image)
        latent["samples"] = latent_image

        noise_mask = None
        if "noise_mask" in latent:
            noise_mask = latent["noise_mask"]

        disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
        samples = guider.sample(noise.generate_noise(latent), latent_image, sampler, sigmas, denoise_mask=noise_mask,
                                callback=self.get_callback(), disable_pbar=disable_pbar, seed=noise.seed)
        samples = samples.to(comfy.model_management.intermediate_device())

        out = latent.copy()
        out["samples"] = samples
        if "x0" in self.x0_output_dict:
            out_denoised = latent.copy()
            out_denoised["samples"] = guider.model_patcher.model.process_latent_out(self.x0_output_dict["x0"].cpu())
        else:
            out_denoised = out
        return (out, out_denoised)


class Func_BasicScheduler(Func):
    def __init__(self, name="BasicScheduler"):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='scheduler', data_type='STRING'),
            IOInfo(name='steps', data_type='INT'),
            IOInfo(name='denoise', data_type='FLOAT'),
        )

        self.set_outputs(
            IOInfo(name='sigmas', data_type='SIGMAS'),
        )

    def run(self, model, scheduler, steps, denoise):
        total_steps = steps
        if denoise < 1.0:
            if denoise <= 0.0:
                return (torch.FloatTensor([]),)
            total_steps = int(steps / denoise)

        sigmas = comfy.samplers.calculate_sigmas(model.get_model_object("model_sampling"), scheduler, total_steps).cpu()
        sigmas = sigmas[-(steps + 1):]
        return (sigmas,)


class Func_KSamplerSelect(Func):
    def __init__(self, name="KSamplerSelect"):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='sampler_name', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='sampler', data_type='SAMPLER'),
        )

    def run(self, sampler_name):
        sampler = comfy.samplers.sampler_object(sampler_name)
        return (sampler,)


class Noise_RandomNoise:
    def __init__(self, seed):
        self.seed = seed

    def generate_noise(self, input_latent):
        latent_image = input_latent["samples"]
        batch_inds = input_latent["batch_index"] if "batch_index" in input_latent else None
        return comfy.sample.prepare_noise(latent_image, self.seed, batch_inds)


class Func_RandomNoise(Func):
    def __init__(self, name="RandomNoise"):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='noise_seed', data_type='INT'),
        )

        self.set_outputs(
            IOInfo(name='noise', data_type='NOISE'),
        )

    def run(self, noise_seed):
        return (Noise_RandomNoise(noise_seed),)


class Guider_Basic(comfy.samplers.CFGGuider):
    def set_conds(self, positive):
        self.inner_set_conds({"positive": positive})


class Func_BasicGuider(Func):
    def __init__(self, name="BasicGuider"):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='conditioning', data_type='CONDITIONING'),
        )

        self.set_outputs(
            IOInfo(name='guider', data_type='GUIDER'),
        )

    def run(self, model, conditioning):
        guider = Guider_Basic(model)
        guider.set_conds(conditioning)
        return (guider,)


class Func_InpaintModelConditioning(Func):
    def __init__(self, name="InpaintModelConditioning"):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
            IOInfo(name='vae', data_type='VAE'),
            IOInfo(name='pixels', data_type='IMAGE'),
            IOInfo(name='mask', data_type='MASK'),
            IOInfo(name='noise_mask', data_type='BOOLEAN'),
        )

        self.set_outputs(
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
            IOInfo(name='latent', data_type='LATENT'),
        )

    def run(self, positive, negative, pixels, vae, mask, noise_mask=False):
        x = (pixels.shape[1] // 8) * 8
        y = (pixels.shape[2] // 8) * 8
        mask = torch.nn.functional.interpolate(mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])),
                                               size=(pixels.shape[1], pixels.shape[2]), mode="bilinear")

        orig_pixels = pixels
        pixels = orig_pixels.clone()
        if pixels.shape[1] != x or pixels.shape[2] != y:
            x_offset = (pixels.shape[1] % 8) // 2
            y_offset = (pixels.shape[2] % 8) // 2
            pixels = pixels[:, x_offset:x + x_offset, y_offset:y + y_offset, :]
            mask = mask[:, :, x_offset:x + x_offset, y_offset:y + y_offset]

        m = (1.0 - mask.round()).squeeze(1)
        for i in range(3):
            pixels[:, :, :, i] -= 0.5
            pixels[:, :, :, i] *= m
            pixels[:, :, :, i] += 0.5
        concat_latent = vae.encode(pixels)
        orig_latent = vae.encode(orig_pixels)

        out_latent = {}

        out_latent["samples"] = orig_latent
        if noise_mask:
            out_latent["noise_mask"] = mask

        out = []
        for conditioning in [positive, negative]:
            c = conditioning_set_values(conditioning, {"concat_latent_image": concat_latent,
                                                       "concat_mask": mask})
            out.append(c)
        return (out[0], out[1], out_latent)


class Func_DifferentialDiffusion(Func):
    def __init__(self, name="DifferentialDiffusion"):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='model', data_type='MODEL'),
        )

        self.set_outputs(
            IOInfo(name='model', data_type='MODEL'),
        )

    def run(self, model):
        model = model.clone()
        model.set_model_denoise_mask_function(self.forward)
        return (model,)

    def forward(self, sigma: torch.Tensor, denoise_mask: torch.Tensor, extra_options: dict):
        model = extra_options["model"]
        step_sigmas = extra_options["sigmas"]
        sigma_to = model.inner_model.model_sampling.sigma_min
        if step_sigmas[-1] > sigma_to:
            sigma_to = step_sigmas[-1]
        sigma_from = step_sigmas[0]

        ts_from = model.inner_model.model_sampling.timestep(sigma_from)
        ts_to = model.inner_model.model_sampling.timestep(sigma_to)
        current_ts = model.inner_model.model_sampling.timestep(sigma[0])

        threshold = (current_ts - ts_to) / (ts_from - ts_to)

        return (denoise_mask >= threshold).to(denoise_mask.dtype)


class Func_LTXVConditioning(Func):
    def __init__(self, name='LTXVConditioning'):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
            IOInfo(name='frame_rate', data_type='FLOAT'),

        )

        self.set_outputs(
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
        )

    def run(self, positive, negative, frame_rate):
        positive = conditioning_set_values(positive, {"frame_rate": frame_rate})
        negative = conditioning_set_values(negative, {"frame_rate": frame_rate})
        return (positive, negative)


class Func_EmptyLTXVLatentVideo(Func):
    def __init__(self, name='EmptyLTXVLatentVideo'):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='width', data_type='INT'),
            IOInfo(name='height', data_type='INT'),
            IOInfo(name='length', data_type='INT'),
        )

        self.set_outputs(
            IOInfo(name='latent', data_type='LATENT'),
        )

    def run(self, width, height, length, batch_size=1):
        latent = torch.zeros([batch_size, 128, ((length - 1) // 8) + 1, height // 32, width // 32],
                             device=comfy.model_management.intermediate_device())
        return ({"samples": latent},)


class Func_LTXVScheduler(Func):
    def __init__(self, name='LTXVScheduler'):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='latent', data_type='LATENT'),
            IOInfo(name='steps', data_type='INT'),
            IOInfo(name='max_shift', data_type='FLOAT'),
            IOInfo(name='base_shift', data_type='FLOAT'),
            IOInfo(name='stretch', data_type='BOOLEAN'),
            IOInfo(name='terminal', data_type='FLOAT'),
        )

        self.set_outputs(
            IOInfo(name='sigmas', data_type='SIGMAS'),
        )

    def run(self, steps, max_shift, base_shift, stretch, terminal, latent=None):
        if latent is None:
            tokens = 4096
        else:
            tokens = math.prod(latent["samples"].shape[2:])

        sigmas = torch.linspace(1.0, 0.0, steps + 1)

        x1 = 1024
        x2 = 4096
        mm = (max_shift - base_shift) / (x2 - x1)
        b = base_shift - mm * x1
        sigma_shift = (tokens) * mm + b

        power = 1
        sigmas = torch.where(
            sigmas != 0,
            math.exp(sigma_shift) / (math.exp(sigma_shift) + (1 / sigmas - 1) ** power),
            0,
        )

        # Stretch sigmas so that its final value matches the given terminal value.
        if stretch:
            non_zero_mask = sigmas != 0
            non_zero_sigmas = sigmas[non_zero_mask]
            one_minus_z = 1.0 - non_zero_sigmas
            scale_factor = one_minus_z[-1] / (1.0 - terminal)
            stretched = 1.0 - (one_minus_z / scale_factor)
            sigmas[non_zero_mask] = stretched

        return (sigmas,)


class Noise_EmptyNoise:
    def __init__(self):
        self.seed = 0

    def generate_noise(self, input_latent):
        latent_image = input_latent["samples"]
        return torch.zeros(latent_image.shape, dtype=latent_image.dtype, layout=latent_image.layout, device="cpu")


class Func_SamplerCustom(Func):

    def __init__(self, name="SamplerCustom", preview_method=LatentPreviewMethod.Auto,
                 preview_steps=3):
        super().__init__(name)

        self.preview_method = preview_method
        self.previewer = None
        self.preview_steps = preview_steps
        self.callback = None
        self.x0_output_dict = {}

        self.set_inputs(
            IOInfo(name='model', data_type='MODEL'),
            IOInfo(name='add_noise', data_type='BOOLEAN'),
            IOInfo(name='noise_seed', data_type='INT'),
            IOInfo(name='cfg', data_type='FLOAT'),
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
            IOInfo(name='sampler', data_type='SAMPLER'),
            IOInfo(name='sigmas', data_type='SIGMAS'),
            IOInfo(name='latent_image', data_type='LATENT'),

        )

        self.set_outputs(
            IOInfo(name='output', data_type='LATENT'),
            IOInfo(name='denoised_output', data_type='LATENT'),
        )

    def set_callback(self, cb):
        self.callback = cb

    def get_callback(self):
        if not self.callback:
            return None

        def _callback(step, x0, x, total_steps):
            """ Return step, total_steps, and preview_bytes. """

            self.x0_output_dict["x0"] = x0

            step += 1
            if step == 1 or step == total_steps or step % self.preview_steps == 0:
                preview_bytes = self.previewer.decode_latent_to_preview_base64(x0)
                self.callback(step, total_steps, preview_bytes)

        return _callback

    def run(self, model, add_noise, noise_seed, cfg, positive, negative, sampler, sigmas, latent_image):

        if not self.previewer:
            self.previewer = get_previewer(self.preview_method, model.load_device, model.model.latent_format)

        latent = latent_image
        latent_image = latent["samples"]
        latent = latent.copy()
        latent_image = comfy.sample.fix_empty_latent_channels(model, latent_image)
        latent["samples"] = latent_image

        if not add_noise:
            noise = Noise_EmptyNoise().generate_noise(latent)
        else:
            noise = Noise_RandomNoise(noise_seed).generate_noise(latent)

        noise_mask = None
        if "noise_mask" in latent:
            noise_mask = latent["noise_mask"]

        disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
        samples = comfy.sample.sample_custom(model, noise, cfg, sampler, sigmas, positive, negative, latent_image,
                                             noise_mask=noise_mask, callback=self.get_callback(),
                                             disable_pbar=disable_pbar, seed=noise_seed)

        out = latent.copy()
        out["samples"] = samples
        if "x0" in self.x0_output_dict:
            out_denoised = latent.copy()
            out_denoised["samples"] = model.model.process_latent_out(self.x0_output_dict["x0"].cpu())
        else:
            out_denoised = out
        return (out, out_denoised)


class Func_SaveAnimatedWEBP(Func):
    def __init__(self, name='SaveAnimatedWEBP'):
        super().__init__(name=name)

        self.methods = {"default": 4, "fastest": 0, "slowest": 6}

        self.set_inputs(
            IOInfo(name='images', data_type='IMAGE'),
            IOInfo(name='fps', data_type='FLOAT'),
            IOInfo(name='lossless', data_type='BOOLEAN'),
            IOInfo(name='quality', data_type='INT'),
            IOInfo(name='method', data_type='STRING'),
        )

        self.set_outputs(
            IOInfo(name='result', data_type='RESULT'),
        )

    @property
    def method_names(self):
        return list(self.methods.keys())

    def run(self, images, fps, lossless, quality, method, num_frames=0):
        assert self.prompt, "Prompt must be set where func registered."

        method = self.methods.get(method)
        results = list()

        pil_images = []
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            pil_images.append(img)

        metadata = pil_images[0].getexif()
        metadata[0x0110] = "prompt:{}".format(json.dumps(self.prompt.model_dump()))

        if num_frames == 0:
            num_frames = len(pil_images)

        c = len(pil_images)
        for i in range(0, c, num_frames):
            file_path = Artwork.create_file_path(media_type='image', ext='.webp')
            pil_images[i].save(file_path, save_all=True, duration=int(1000.0 / fps),
                               append_images=pil_images[i + 1:i + num_frames], exif=metadata, lossless=lossless,
                               quality=quality, method=method)

            meta_info = get_meta_info(file_path)
            artwork = Artwork.add_art_work(
                file_path=file_path,
                card_name=self.prompt.card_name,
                media_type='image',
                meta_info=meta_info,
                prompt=self.prompt,
            )
            results.append(artwork)

        return ({"images": results},)


class Func_LTXVImgToVideo(Func):
    def __init__(self, name='LTXVImgToVideo'):
        super().__init__(name=name)

        self.set_inputs(
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
            IOInfo(name='vae', data_type='VAE'),
            IOInfo(name='image', data_type='IMAGE'),

            IOInfo(name='width', data_type='INT'),
            IOInfo(name='height', data_type='INT'),
            IOInfo(name='length', data_type='INT'),
        )

        self.set_outputs(
            IOInfo(name='positive', data_type='CONDITIONING'),
            IOInfo(name='negative', data_type='CONDITIONING'),
            IOInfo(name='latent', data_type='LATENT'),
        )

    def run(self, positive, negative, image, vae, width, height, length, batch_size=1):
        pixels = comfy.utils.common_upscale(image.movedim(-1, 1), width, height, "bilinear", "center").movedim(1, -1)
        encode_pixels = pixels[:, :, :, :3]
        t = vae.encode(encode_pixels)
        positive = conditioning_set_values(positive, {"guiding_latent": t})
        negative = conditioning_set_values(negative, {"guiding_latent": t})

        latent = torch.zeros([batch_size, 128, ((length - 1) // 8) + 1, height // 32, width // 32],
                             device=comfy.model_management.intermediate_device())
        latent[:, :, :t.shape[2]] = t
        return (positive, negative, {"samples": latent},)


class Func_EmptyMochiLatentVideo(Func):
    def __init__(self, name='EmptyMochiLatentVideo'):
        super().__init__(name)

        self.set_inputs(
            IOInfo(name='width', data_type='INT'),
            IOInfo(name='height', data_type='INT'),
            IOInfo(name='length', data_type='INT'),

        )

        self.set_outputs(
            IOInfo(name='latent', data_type='LATENT'),
        )

    def run(self, width, height, length, batch_size=1):
        latent = torch.zeros([batch_size, 12, ((length - 1) // 6) + 1, height // 8, width // 8],
                             device=comfy.model_management.intermediate_device())
        return ({"samples": latent},)
