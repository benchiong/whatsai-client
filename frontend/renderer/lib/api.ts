import { WidgetImageSchema, WidgetType } from "../data-type/widget";
import {
  CardInfoSchema,
  CardInfoType,
  SimpleCardInfoArraySchema,
  SimpleCardInfoArrayType,
} from "../data-type/card";
import { z } from "zod";
import {
  DownloadingModelTaskArraySchema,
  DownloadingModelTaskArrayType,
  FrontModelDirType,
  mapModelDirSchema2FrontModelDirSchema,
  ModelDirSchema,
  ModelInfoArraySchema,
  ModelInfoArrayType,
  ModelInfoListSchema,
  ModelInfoListType,
  ModelInfoSchema,
  ModelInfoType,
} from "../data-type/model";
import {
  MediaArraySchema,
  MediaArrayType,
  MediaSchema,
  MediaType,
} from "../data-type/media";
import { AddonSchema, AddonType } from "../data-type/addons";
import { TaskArraySchema, TaskArrayType } from "../data-type/task";
import {
  ArtworkArraySchema,
  ArtworkSchema,
  ArtworkType,
} from "../data-type/artwork";
import {
  CivitaiFileToDownLoadArrayType,
  CivitaiModelVersionSchema,
  CivitaiModelVersionType,
} from "../data-type/civitai-data-type";

let serverUrl = "http://127.0.0.1:8172/";

export function setServeUrl(url: string) {
  serverUrl = url;
  console.log(serverUrl);
}

export async function home(): Promise<any> {
  const res = await fetch(serverUrl, {
    method: "GET",
  });
  return await res.json();
}

export async function cardDemo(): Promise<any> {
  const res = await fetch(serverUrl + "card_demo", {
    method: "GET",
  });
  return await res.json();
}

export async function widget(): Promise<WidgetType | null> {
  try {
    const res = await fetch(serverUrl + "test_widget", {
      method: "GET",
    });
    const resp = await res.json();
    const result = WidgetImageSchema.safeParse(resp);
    if (result.success) {
      return result.data;
    } else {
      console.log(result.error.issues);
      return null;
    }
  } catch (e) {
    console.error(e);
    return null;
  }
}

export async function localFile(path: string) {
  if (!path) {
    return null;
  }
  const resp = await fetch(serverUrl + `local_file/?path=${path}`, {
    method: "GET",
  });

  const blob = await resp.blob();
  return blob ?? null;
}

export async function listModels(
  funcName: string,
  extraParams: any = null,
): Promise<ModelInfoListType> {
  try {
    const url = serverUrl + "list_models/";

    const data = {
      func_name: funcName,
      extra_params: extraParams,
    };
    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    const r = ModelInfoListSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return [] as ModelInfoListType;
    }
  } catch (e) {
    console.log(e);
    return [] as ModelInfoListType;
  }
}

export const AddonInfoRespSchema = z.object({
  errorMessage: z.string().nullable(),
  addon_info: AddonSchema,
});
export type WidgetInfoListResp = z.infer<typeof AddonInfoRespSchema>;

export async function getAddonWidgetInfos(
  addonName: string,
): Promise<AddonType | null> {
  try {
    const resp = await fetch(serverUrl + `addon/addon_info/${addonName}`, {
      method: "GET",
    });
    const res = await resp.json();
    const r = AddonInfoRespSchema.safeParse(res);
    if (r.success) {
      return r.data.addon_info;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function getRecentlyUsed(
  mediaType: string,
  subKey: string,
): Promise<MediaArrayType> {
  try {
    const resp = await fetch(
      serverUrl + `recently_used?media_type=${mediaType}&sub_key=${subKey}`,
      {
        method: "GET",
      },
    );
    const res = await resp.json();
    const r = MediaArraySchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return [];
    }
  } catch (e) {
    return [] as MediaArrayType;
  }
}

export async function addRecentlyUsed(
  mediaType: string,
  subKey: string,
  localPath: string,
): Promise<MediaType | null> {
  try {
    const url = serverUrl + "add_recently_used/";

    const data = {
      media_type: mediaType,
      sub_key: subKey,
      local_path: localPath,
    };
    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    const r = MediaSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function removeRecentlyUsed(
  mediaType: string,
  subKey: string,
  localPath: string,
): Promise<MediaArrayType | null> {
  try {
    const url = serverUrl + "remove_recently_used/";

    const data = {
      media_type: mediaType,
      sub_key: subKey,
      local_path: localPath,
    };
    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    const r = MediaArraySchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function execute(prompt: object) {
  try {
    const url = serverUrl + "execution?client_id=1bc";
    const data = {
      ...prompt,
    };
    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    return res;
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function getAllCards(): Promise<SimpleCardInfoArrayType> {
  try {
    const resp = await fetch(serverUrl + "card/all_cards", {
      method: "GET",
    });
    const res = await resp.json();
    const r = SimpleCardInfoArraySchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return [];
    }
  } catch (e) {
    return [];
  }
}

export const LocalCardInfoResponseSchema = z.object({
  errorMessage: z.string().nullable(),
  cardInfo: CardInfoSchema.nullable(),
});

export type LocalCardInfoResponse = z.infer<typeof LocalCardInfoResponseSchema>;

export async function getCardInfo(
  cardName: String,
): Promise<LocalCardInfoResponse> {
  try {
    const res = await fetch(serverUrl + `card/local_card_info/${cardName}`, {
      method: "GET",
    });
    const resp = await res.json();

    if (resp["errorMessage"]) {
      return {
        errorMessage: resp["errorMessage"],
        cardInfo: null,
      };
    }
    const cardInfo = resp["cardInfo"];
    const r = CardInfoSchema.safeParse(cardInfo);
    if (r.success) {
      return {
        errorMessage: null,
        cardInfo: r.data,
      };
    } else {
      console.log("issues:", r.error.issues);

      return {
        errorMessage: "" + r.error,
        cardInfo: null,
      };
    }
  } catch (e) {
    console.error(e);
    return {
      errorMessage: "" + e,
      cardInfo: null,
    };
  }
}

export async function updateCardCache(
  cardName: string,
  cardInfo: CardInfoType | null = null,
): Promise<LocalCardInfoResponse | null> {
  try {
    const url = serverUrl + "card/cache_card_prompt/";

    const data = {
      card_name: cardName,
      card_info: cardInfo,
    };

    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
        Pragma: "no-cache",
      },
    });
    const res = await result.json();
    const r = LocalCardInfoResponseSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function generate(
  cardName: string,
  clientId: string,
): Promise<Boolean> {
  try {
    const url = serverUrl + "generate";

    const data = {
      card_name: cardName,
      client_id: clientId,
    };

    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    const r = z.boolean().safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return false;
    }
  } catch (e) {
    console.log(e);
    return false;
  }
}

export async function getTasks(): Promise<TaskArrayType> {
  try {
    const resp = await fetch(serverUrl + "task/get_tasks", {
      method: "GET",
    });
    const res = await resp.json();
    const r = TaskArraySchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return [];
    }
  } catch (e) {
    return [];
  }
}

export async function removeTask(taskId: number): Promise<Boolean> {
  if (!taskId) {
    return false;
  }
  try {
    const resp = await fetch(serverUrl + `task/remove_task?task_id=${taskId}`, {
      method: "GET",
    });
    return await resp.json();
  } catch (e) {
    return false;
  }
}

const ArtworksResponseSchema = z.object({
  artworks: ArtworkArraySchema,
  page_num: z.number(),
  has_next: z.boolean(),
});

type ArtworksResponseType = z.infer<typeof ArtworksResponseSchema>;

export async function getArtworks(
  pageNumber: number,
): Promise<ArtworksResponseType | null> {
  try {
    const resp = await fetch(
      serverUrl + `art/get_artworks?page_num=${pageNumber}`,
      {
        method: "GET",
      },
    );
    const res = await resp.json();
    const r = ArtworksResponseSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    return null;
  }
}

export async function getArtwork(
  artworkId: number,
): Promise<ArtworkType | null> {
  try {
    const res = await fetch(
      serverUrl + `art/get_artwork/?artwork_id=${artworkId}`,
      {
        method: "GET",
      },
    );
    const resp = await res.json();
    if (!resp) {
      return null;
    }
    const r = ArtworkSchema.safeParse(resp);
    if (r.success) {
      return r.data;
    } else {
      console.log("issues:", r.error.issues);
      return null;
    }
  } catch (e) {
    console.error(e);
    return null;
  }
}

export const ModelTypesSchema = z.array(z.string());
export type ModelTypesType = z.infer<typeof ModelTypesSchema>;

export async function getAllModelTypes(): Promise<ModelTypesType> {
  try {
    const resp = await fetch(serverUrl + "model/get_all_model_types", {
      method: "GET",
    });
    const res = await resp.json();
    const r = ModelTypesSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return [];
    }
  } catch (e) {
    return [];
  }
}

export async function syncModelInfos(
  modelType: string,
): Promise<ModelInfoListType> {
  try {
    const url = serverUrl + "model/sync_model_infos";

    const data = {
      model_type: modelType,
    };

    const resp = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await resp.json();
    const r = ModelInfoListSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return [];
    }
  } catch (e) {
    return [];
  }
}

export async function getModels(): Promise<ModelInfoArrayType> {
  try {
    const resp = await fetch(serverUrl + "model/get_all_models", {
      method: "GET",
    });
    const res = await resp.json();
    const r = ModelInfoArraySchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return [];
    }
  } catch (e) {
    return [];
  }
}

export async function getModelByModelId(
  modelId: string,
): Promise<ModelInfoType | null> {
  try {
    const resp = await fetch(
      serverUrl + `model/get_model_by_model_id?model_id=${modelId}`,
      {
        method: "GET",
      },
    );
    const res = await resp.json();
    if (!res) {
      return null;
    }
    const r = ModelInfoSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function getModelByModelLocalPath(
  localPath: string,
): Promise<ModelInfoType | null> {
  try {
    const resp = await fetch(
      serverUrl + `model/get_model_by_local_path?local_path=${localPath}`,
      {
        method: "GET",
      },
    );
    const res = await resp.json();
    if (!res) {
      return null;
    }
    const r = ModelInfoSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function downloadCivitaiModel(
  filesToDownload: CivitaiFileToDownLoadArrayType,
  modelVersionInfo: CivitaiModelVersionType,
  imageToDownload: string,
): Promise<any> {
  try {
    const url = serverUrl + "model/download_civitai_model";

    const data = {
      civitai_model_version: modelVersionInfo,
      files_to_download: filesToDownload,
      image_to_download: imageToDownload,
    };

    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    return await result.json();
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function downloadHuggingfaceModel(
  urlToDownload: string,
  modelType: string,
): Promise<any> {
  try {
    const url = serverUrl + "model/download_huggingface_model";

    const data = {
      url_to_download: urlToDownload,
      model_type: modelType,
    };

    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    return await result.json();
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function getModelDir(
  modelType: string,
): Promise<FrontModelDirType | null> {
  try {
    const resp = await fetch(serverUrl + `model/model_dir/${modelType}`, {
      method: "GET",
    });
    const res = await resp.json();
    const r = ModelDirSchema.safeParse(res);
    if (r.success) {
      const serverData = r.data;
      return mapModelDirSchema2FrontModelDirSchema(serverData);
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    return null;
  }
}

export const ModelDirRespSchema = z.object({
  success: z.boolean(),
  error_info: z.string().nullable(),
  record: ModelDirSchema.nullable(),
});

export type ModelDirRespType = z.infer<typeof ModelDirRespSchema>;

export async function addModelDir(
  modelType: string,
  modelDir: string,
  setAsDefault: boolean = false,
): Promise<ModelDirRespType | null> {
  try {
    const url = serverUrl + "model/model_dir/add_model_dir";

    const data = {
      model_type: modelType,
      model_dir: modelDir,
      set_as_default: setAsDefault,
      register_model_type_if_not_exists: false,
    };

    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    const r = ModelDirRespSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function removeModelDir(
  modelType: string,
  modelDir: string,
): Promise<ModelDirRespType | null> {
  try {
    const url = serverUrl + "model/model_dir/remove_model_dir";

    const data = {
      model_type: modelType,
      model_dir: modelDir,
    };

    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    const r = ModelDirRespSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function setDefaultModelDir(
  modelType: string,
  modelDir: string,
): Promise<ModelDirRespType | null> {
  try {
    const url = serverUrl + "model/model_dir/set_default_model_dir";

    const data = {
      model_type: modelType,
      model_dir: modelDir,
    };

    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    const r = ModelDirRespSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export async function isDirOk(dirName: string) {
  try {
    const resp = await fetch(
      serverUrl + `utils/is_dir_path_ok?dir_path=${dirName}`,
      {
        method: "GET",
      },
    );
    return await resp.json();
  } catch (e) {
    console.error(e);
    return false;
  }
}

export async function getOtherUIPathMap(UIName: string) {
  try {
    const resp = await fetch(
      serverUrl +
        `model/model_dir/get_other_ui_model_paths_map?ui_name=${UIName}`,
      {
        method: "GET",
      },
    );
    return await resp.json();
  } catch (e) {
    console.error(e);
    return null;
  }
}

export const AddOtherUIDirsRespSchema = z.object({
  added_paths: z.array(z.array(z.string())).nullable(),
  info: z.string().nullable(),
});

export type AddOtherUIDirsRespType = z.infer<typeof AddOtherUIDirsRespSchema>;
export async function addOtherUIDirs(
  UIName: string,
  UIBaseDir: string,
  setAsDefault: boolean = false,
): Promise<AddOtherUIDirsRespType | null> {
  try {
    const url = serverUrl + "model/model_dir/add_other_ui_model_paths";

    const data = {
      ui_name: UIName,
      ui_dir: UIBaseDir,
      set_as_default: setAsDefault,
    };

    const result = await fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    const res = await result.json();
    console.log("resp", res);
    const r = AddOtherUIDirsRespSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return null;
    }
  } catch (e) {
    console.log(e);
    return null;
  }
}

export const CivitaiModelVersionInfoRespSchema = z.object({
  model_version_info: CivitaiModelVersionSchema.nullable(),
  error: z.string().nullable(),
});

export type CivitaiModelVersionInfoRespType = z.infer<
  typeof CivitaiModelVersionInfoRespSchema
>;
export async function getCivitaiModelVersionInfo(
  url: string,
  useCache: boolean = true,
): Promise<CivitaiModelVersionInfoRespType> {
  try {
    const resp = await fetch(
      serverUrl +
        `civitai/get_civitai_model_version_info_with_url?url_str=${url}&use_cache=${useCache}`,
      {
        method: "GET",
      },
    );
    const res = await resp.json();
    const r = CivitaiModelVersionInfoRespSchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return {
        model_version_info: null,
        error: r.error.issues.toString(),
      };
    }
  } catch (e) {
    console.error(e);
    return CivitaiModelVersionInfoRespSchema.parse({
      model_version_info: null,
      error: "Unknown error.",
    });
  }
}

export async function getHuggingfaceModelVersionInfo(
  url: string,
): Promise<number | null> {
  try {
    const resp = await fetch(
      serverUrl + `model/get_huggingface_model_size?url_to_download=${url}`,
      {
        method: "GET",
      },
    );
    return await resp.json();
  } catch (e) {
    console.error(e);
    return null;
  }
}

export async function getDownloadingInfos(): Promise<DownloadingModelTaskArrayType> {
  try {
    const resp = await fetch(serverUrl + "model/get_downloading_models", {
      method: "GET",
    });
    const res = await resp.json();
    const r = DownloadingModelTaskArraySchema.safeParse(res);
    if (r.success) {
      return r.data;
    } else {
      console.log(r.error.issues);
      return [];
    }
  } catch (e) {
    return [];
  }
}

export async function cancelDownloadTask(taskId: string): Promise<boolean> {
  try {
    const resp = await fetch(
      serverUrl + `model/cancel_downloading_task?task_id=${taskId}`,
      {
        method: "GET",
      },
    );
    return await resp.json();
  } catch (e) {
    return false;
  }
}
