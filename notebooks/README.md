# Model experiments (owned separately)

Member 2: Create `controlnet.ipynb` for Depth Anything V2 + StableDiffusionControlNetImg2ImgPipeline.
Model: https://huggingface.co/lllyasviel/sd-controlnet-depth
Docs: https://huggingface.co/docs/diffusers/api/pipelines/controlnet

Member 3: Create `ic_light.ipynb` or wrapper for the original IC-Light demo.
Source: https://github.com/lllyasviel/IC-Light
Important: This model is trained for foreground relighting and might fail for outdoor whole-street scenes. Do not claim preservation until visually verified.

Use a Colab GPU or a suitable local GPU. Store model weights in the runtime or cache, not in this repository.
Output PNG files go into the local outputs folder or an access-controlled team shared folder, provided their license allows reuse.
