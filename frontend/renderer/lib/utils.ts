import { ModelsRecordType } from "../data-type/model";

export function capitalizeFirstLetter(str: string): string {
  return str.substring(0, 1).toUpperCase() + str.substring(1);
}

export const getKeyOfModelsRecord = (modelsRecord: ModelsRecordType) => {
  return Object.keys(modelsRecord)[0];
};

export type CivitAI2WhatsAIMapType = {
  [key: string]: string;
};

// todo: not sure it's all cases covered.
const civitai2whatsaiMap: CivitAI2WhatsAIMapType = {
  Checkpoint: "checkpoint",
  TextualInversion: "embedding",
  Hypernetwork: "hypernet",
  LORA: "lora",
  LoCon: "lora",
  DoRA: "lora",
  Controlnet: "controlnet",
  Upscaler: "upscaler",
  VAE: "vae",
  Poses: "controlnet",
  AestheticGradient: "others",
  Wildcards: "others",
};

export const mapCivitaiModelTypeToWhatsAI = (
  civitAIModelType: string,
): string => {
  return civitai2whatsaiMap[civitAIModelType] ?? "others";
};
