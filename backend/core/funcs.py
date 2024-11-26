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
from core.abstracts import Func
from tiny_db.artwork import ArtworkTable
from tiny_db.model_dir import ModelDirTable
from tiny_db.model_info import ModelInfoTable
from core.extras import tae_model_info_list
from misc.helpers import pillow
from misc.logger import logger

try:
    from spandrel_extra_arches import EXTRA_REGISTRY
    from spandrel import MAIN_REGISTRY, ModelLoader, ImageModelDescriptor

    MAIN_REGISTRY.add(*EXTRA_REGISTRY)
    logger.info("Successfully imported spandrel_extra_arches.")
except Exception as e:
    logger.debug("Fail to imported spandrel_extra_arches: {}".format(e))

class Func_CheckpointLoaderSimple(Func):
    def __init__(self, name="Checkpoint Loader", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, checkpoint_hash):
        model_record = ModelInfoTable.sync_get_model_info_by_hash(checkpoint_hash)
        checkpoint_path = model_record.get('local_path')
        embedding_directories = ModelDirTable.sync_get_model_dirs('embedding')
        out = comfy.sd.load_checkpoint_guess_config(
            checkpoint_path,
            output_vae=True,
            output_clip=True,
            embedding_directory=embedding_directories
        )
        return out[:3]

class Func_VAELoader(Func):
    def __init__(self, name="Load VAE", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, vae_model):
        tae_model_infos = tae_model_info_list()
        is_vae_model_tae = False

        for tae_model in tae_model_infos:
            if tae_model.get('local_path') == vae_model.get('local_path'):
                is_vae_model_tae = True
                break
        if is_vae_model_tae:
            sd = self.load_taesd(vae_model)
        else:
            vae_path = vae_model.get('local_path')
            sd = comfy.utils.load_torch_file(vae_path)
        vae = comfy.sd.VAE(sd=sd)
        return vae

    def load_taesd(self, vae_model):
        encoder_path, decoder_path = vae_model.get('local_path').split('|')
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
    def __init__(self, name="Clip Text Encoder", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, clip, text):
        tokens = clip.tokenize(text)
        output = clip.encode_from_tokens(tokens, return_pooled=True, return_dict=True)
        cond = output.pop("cond")
        # print(type(cond), type(output), output.keys(), [type(v) for v in output.values()])
        # <class 'torch.Tensor'> <class 'dict'> dict_keys(['pooled_output']) [<class 'torch.Tensor'>]
        return [[cond, output]]


class Func_EmptyLatentImage(Func):
    def __init__(self, name=None, cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.device = comfy.model_management.intermediate_device()

    def run(self, width: int, height: int, batch_size: int = 1):
        latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        return {"samples": latent}


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
    return out

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
    def __init__(self, latent_rgb_factors):
        self.latent_rgb_factors = torch.tensor(latent_rgb_factors, device="cpu")

    def decode_latent_to_preview_base64(self, x0):
        self.latent_rgb_factors = self.latent_rgb_factors.to(dtype=x0.dtype, device=x0.device)
        latent_image = x0[0].permute(1, 2, 0) @ self.latent_rgb_factors
        return preview_to_base64(latent_image)

def get_previewer(preview_method, device, latent_format):
    previewer = None
    if latent_format.taesd_decoder_name is not None and not preview_method == LatentPreviewMethod.Latent2RGB:
        tae_file_records = ModelInfoTable.sync_get_taesd_file_records()
        tae_file_record = None
        for f in tae_file_records:
            if f.get('file_name').startswith(latent_format.taesd_decoder_name):
                tae_file_record = f
                break
        if tae_file_record:
            tae_file_path = tae_file_record.get('local_path')
            taesd = TAESD(None, tae_file_path, latent_channels=latent_format.latent_channels).to(device)
            previewer = TAESDPreviewerImpl(taesd)
    else:
        previewer = Latent2RGBPreviewer(latent_format.latent_rgb_factors)
    return previewer

class Func_KSampler(Func):
    def __init__(self,
                 name='kSample',
                 cache_out=True,
                 valid_inputs=True,
                 preview_method=LatentPreviewMethod.Auto,
                 preview_steps=3
                 ):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)
        self.preview_method = preview_method
        self.previewer = None
        self.preview_steps = preview_steps

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
            callback = None,
            ):

        if not self.previewer:
            self.previewer = get_previewer(self.preview_method, model.load_device, model.model.latent_format)

        def _callback(step, x0, x, total_steps):
            step += 1
            if step == 1 or step == total_steps or step % self.preview_steps == 0:
                preview_bytes = self.previewer.decode_latent_to_preview_base64(x0)
                if callback:
                    callback(step, total_steps, preview_bytes)

        return common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image,
                               denoise=denoise, callback=_callback)

class Func_KSamplerAdvanced(Func):
    def __init__(self,
                 name='KSamplerAdvanced',
                 cache_out=True,
                 valid_inputs=True,
                 preview_method=LatentPreviewMethod.Auto,
                 preview_steps=3
                 ):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)
        self.preview_method = preview_method
        self.previewer = None
        self.preview_steps = preview_steps

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
                               last_step=end_at_step, force_full_denoise=force_full_denoise, callback=_callback)


class Func_VAEDecode(Func):
    def __init__(self, name="Vae Decode", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, vae, samples):
        return vae.decode(samples["samples"])

class Func_VAEEncode(Func):
    def __init__(self, name="Vae Encode", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, vae, pixels):
        t = vae.encode(pixels[:, :, :, :3])
        return {"samples": t}


class Func_SaveImage(Func):
    def __init__(self, name="Save Image", cache_out=False, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

        self.prefix_append = ""
        self.compress_level = 4

    def run(self,
            images: Tensor,
            card_info: dict | None = None,
            inputs_info: dict | None = None,
            addon_inputs_info: dict | None = None,
            meta_info: dict | None = None
            ):
        results = list()

        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            metadata = PngInfo()
            metadata.add_text("card_info", json.dumps(card_info))
            metadata.add_text("inputs_info", json.dumps(inputs_info))
            metadata.add_text("addon_inputs_info", json.dumps(addon_inputs_info))

            filename = ArtworkTable.get_file_name(media_type='image')
            img.save(filename, pnginfo=metadata, compress_level=self.compress_level)

            art_meta_info = {
                'width': inputs_info.get('width') if inputs_info else None,
                'height': inputs_info.get('height') if inputs_info else None
            } if not meta_info else meta_info

            art = ArtworkTable.add_art(
                card_name=card_info.get('card_name') if card_info else None,
                file_path=filename,
                media_type='image',
                meta_info=art_meta_info,
                # card_info=card_info,
                inputs_info=inputs_info,
                addon_inputs_info=addon_inputs_info
            )
            results.append(art)

        return {"images": results}


class Func_CLIPSetLastLayer(Func):
    def __init__(self, name="Clip Skip", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, clip, stop_at_clip_layer):
        clip = clip.clone()
        clip.clip_layer(stop_at_clip_layer)
        return clip


class Func_LoraLoader(Func):
    def __init__(self, name="LoRA Loader", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self,
            model: comfy.model_patcher.ModelPatcher,
            clip: comfy.sd.CLIP,
            lora_hash: str,
            strength_model: float,
            strength_clip: float
            ):
        if strength_model == 0 and strength_clip == 0:
            return model, clip

        lora_path = ModelInfoTable.sync_get_model_info_by_hash(lora_hash).get("local_path")
        lora = comfy.utils.load_torch_file(lora_path, safe_load=True)

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)
        return model_lora, clip_lora

class Func_UpscaleModelLoader(Func):
    def __init__(self, name="Load Upscale Model", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, model_hash: str):
        model_record = ModelInfoTable.sync_get_model_info_by_hash(model_hash)
        model_path = model_record.get('local_path')

        sd = comfy.utils.load_torch_file(model_path, safe_load=True)
        if "module.layers.0.residual_group.blocks.0.norm1.weight" in sd:
            sd = comfy.utils.state_dict_prefix_replace(sd, {"module.": ""})
        out = ModelLoader().load_from_state_dict(sd).eval()

        if not isinstance(out, ImageModelDescriptor):
            raise Exception("Upscale model must be a single-image model.")

        return out

class Func_ImageUpscaleWithModel(Func):
    def __init__(self, name="Upscale Image (using Model)", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

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
        return s

class Func_ImageScale(Func):
    def __init__(self, name="Upscale Image", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, image, upscale_method, width, height, crop):
        if width == 0 and height == 0:
            s = image
        else:
            samples = image.movedim(-1, 1)

            if width == 0:
                width = max(1, round(samples.shape[3] * height / samples.shape[2]))
            elif height == 0:
                height = max(1, round(samples.shape[2] * width / samples.shape[3]))

            s = comfy.utils.common_upscale(samples, width, height, upscale_method, crop)
            s = s.movedim(1, -1)
        return s

class Func_LatentScale(Func):
    def __init__(self, name="Upscale Latent", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

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
        return s

class Func_LoadImage(Func):
    def __init__(self, name="Load Image", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

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
    def __init__(self, name="Hypernet Loader", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, model, hypernet_hash, strength):
        hypernet_record = ModelInfoTable.sync_get_model_info_by_hash(hypernet_hash)
        hypernet_path = hypernet_record.get('local_path')
        model_hypernet = model.clone()
        patch = self.load_hypernetwork_patch(hypernet_path, strength)
        if patch is not None:
            model_hypernet.set_model_attn1_patch(patch)
            model_hypernet.set_model_attn2_patch(patch)
        return model_hypernet

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

class Func_VAEEncodeForInpainting(Func):
    def __init__(self, name="Vae Encode For Inpainting", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, vae, pixels, mask, grow_mask_by=6):
        x = (pixels.shape[1] // vae.downscale_ratio) * vae.downscale_ratio
        y = (pixels.shape[2] // vae.downscale_ratio) * vae.downscale_ratio
        mask = torch.nn.functional.interpolate(mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])), size=(pixels.shape[1], pixels.shape[2]), mode="bilinear")

        pixels = pixels.clone()
        if pixels.shape[1] != x or pixels.shape[2] != y:
            x_offset = (pixels.shape[1] % vae.downscale_ratio) // 2
            y_offset = (pixels.shape[2] % vae.downscale_ratio) // 2
            pixels = pixels[:, x_offset:x + x_offset, y_offset:y + y_offset, :]
            mask = mask[:, :, x_offset:x + x_offset, y_offset:y + y_offset]

        #grow mask by a few pixels to keep things seamless in latent space
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

        return {
            "samples": t,
            "noise_mask": (mask_erosion[:, :, :x, :y].round())
        }

class Func_ImagePadForOutpainting(Func):
    def __init__(self, name="Image Pad For Outpainting", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

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
    def __init__(self, name="ContronlNet Loader", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, controlnet_hash):
        controlnet_path = ModelInfoTable.sync_get_model_info_by_hash(controlnet_hash).get('local_path')
        controlnet = comfy.controlnet.load_controlnet(controlnet_path)
        return controlnet

class Func_ControlNetApply(Func):
    def __init__(self, name="Apply ControlNet", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

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
        return c


class Func_ClipLoader(Func):
    def __init__(self, name="CLIP Loader", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, clip_hash, type="stable_diffusion"):
        clip_path = ModelInfoTable.sync_get_model_info_by_hash(clip_hash).get('local_path')
        embedding_directories = ModelDirTable.sync_get_model_dirs('embedding')

        if type == "stable_cascade":
            clip_type = comfy.sd.CLIPType.STABLE_CASCADE
        elif type == "sd3":
            clip_type = comfy.sd.CLIPType.SD3
        elif type == "stable_audio":
            clip_type = comfy.sd.CLIPType.STABLE_AUDIO
        else:
            clip_type = comfy.sd.CLIPType.STABLE_DIFFUSION

        clip = comfy.sd.load_clip(ckpt_paths=[clip_path],
                                  embedding_directory=embedding_directories, clip_type=clip_type)
        return clip

class Func_DualCLIPLoader(Func):
    def __init__(self, name="Dual CLIP Loader", cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, clip_hash1, clip_hash2, type):

        clip_path1 = ModelInfoTable.sync_get_model_info_by_hash(clip_hash1).get('local_path')
        clip_path2 = ModelInfoTable.sync_get_model_info_by_hash(clip_hash2).get('local_path')
        embedding_directories = ModelDirTable.sync_get_model_dirs('embedding')

        if type == "sdxl":
            clip_type = comfy.sd.CLIPType.STABLE_DIFFUSION
        elif type == "sd3":
            clip_type = comfy.sd.CLIPType.SD3
        elif type == "flux":
            clip_type = comfy.sd.CLIPType.FLUX

        clip = comfy.sd.load_clip(ckpt_paths=[clip_path1, clip_path2],
                                  embedding_directory=embedding_directories, clip_type=clip_type)
        return clip

class Func_TripleCLIPLoader(Func):
    def __init__(self, name='Triple CLIP Loader', cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, clip_hash1, clip_hash2, clip_hash3):
        clip_path1 = ModelInfoTable.sync_get_model_info_by_hash(clip_hash1).get('local_path')
        clip_path2 = ModelInfoTable.sync_get_model_info_by_hash(clip_hash2).get('local_path')
        clip_path3 = ModelInfoTable.sync_get_model_info_by_hash(clip_hash3).get('local_path')
        embedding_directories = ModelDirTable.sync_get_model_dirs('embedding')

        clip = comfy.sd.load_clip(ckpt_paths=[clip_path1, clip_path2, clip_path3], embedding_directory=embedding_directories)
        return clip

class Func_UNETLoader(Func):
    def __init__(self, name='UNET Loader', cache_out=True, valid_inputs=True):
        super().__init__(name=name, cache_out=cache_out, valid_inputs=valid_inputs)

    def run(self, unet_hash, weight_dtype):
        unet_path = ModelInfoTable.sync_get_model_info_by_hash(unet_hash).get('local_path')

        model_options = {}
        if weight_dtype == "fp8_e4m3fn":
            model_options["dtype"] = torch.float8_e4m3fn
        elif weight_dtype == "fp8_e5m2":
            model_options["dtype"] = torch.float8_e5m2

        model = comfy.sd.load_diffusion_model(unet_path, model_options=model_options)
        return model