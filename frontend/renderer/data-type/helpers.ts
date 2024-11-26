import { ModelInfoType } from "./model";

export function displayNameOfModelInfo(modelInfo: ModelInfoType) {
  const civitaiModelVersion = modelInfo.civit_model;
  if (!civitaiModelVersion) {
    return modelInfo.file_name;
  }
  const civitaiModelName = civitaiModelVersion.model?.name;
  const civitaiModelVersionName = civitaiModelVersion.name;

  if (civitaiModelName) {
    return `${civitaiModelName} - ${civitaiModelVersionName}`;
  } else {
    return `${civitaiModelVersionName}`;
  }
}

export function civitaiUrl(modelInfo: ModelInfoType) {
  const civitaiModelVersion = modelInfo.civit_model;
  const modelId = civitaiModelVersion?.modelId;
  const versionId = civitaiModelVersion?.id;

  if (modelId && versionId) {
    return `https://civitai.com/models/${modelId}?modelVersionId=${versionId}`;
  }
  if (modelId) {
    return `https://civitai.com/models/${modelId}`;
  }
  return null;
}

export const civitSizeStr = (size: number, fix: number = 2) => {
  if (size < 1024 * 1024) {
    // less than 1 GB
    return `${(size / 1024).toFixed(fix)}MB`;
  } else {
    return `${(size / 1024 / 1024).toFixed(fix)}GB`;
  }
};
