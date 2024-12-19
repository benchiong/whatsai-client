import { z } from "zod";
import { CivitaiModelVersionSchema } from "./civitai-data-type";

export const ModelInfoSchema = z.object({
  local_path: z.string(),
  file_name: z.string(),
  sha_256: z.string().nullable(),
  model_type: z.string(),

  // civit_model is Civitai Model Version Info actually.
  // too cost to make it right, leave it as history problem :(
  civit_model: CivitaiModelVersionSchema.optional().nullable(),
  image_path: z.string().nullable(),
  size_kb: z.number().nullable(),

  created_time_stamp: z.number().nullable(),
  created_datetime_str: z.string().nullable(),

  order_num: z.number().nullable(),
});

export type ModelInfoType = z.infer<typeof ModelInfoSchema>;

export const ModelsRecordSchema = z.record(z.array(ModelInfoSchema));
export type ModelsRecordType = z.infer<typeof ModelsRecordSchema>;

export const ModelInfoArraySchema = z.array(ModelsRecordSchema);

export type ModelInfoArrayType = z.infer<typeof ModelInfoArraySchema>;

export const DirInfoSchema = z.object({
  dir: z.string(),
  model_count: z.number(),
  is_default: z.boolean(),
});

export type DirInfoType = z.infer<typeof DirInfoSchema>;

// data type return by server
export const ModelDirSchema = z.object({
  model_type: z.string(),
  dirs: z.array(z.string()),
  default_dir: z.string(),
  counts: z.array(z.number()),
});

export type ModelDirType = z.infer<typeof ModelDirSchema>;

// data type frontend used
export const FrontModelDirSchema = z.object({
  model_type: z.string(),
  dirs: z.array(DirInfoSchema),
  default_dir: z.string(),
});

export type FrontModelDirType = z.infer<typeof FrontModelDirSchema>;

export function mapModelDirSchema2FrontModelDirSchema(modelDir: ModelDirType) {
  const { dirs, counts, default_dir } = modelDir;
  let front_dirs = [];
  for (let i = 0; i < dirs.length; i++) {
    const is_default = dirs[i] == default_dir;
    const frontDir = {
      dir: dirs[i],
      model_count: counts[i],
      is_default: is_default,
    };
    front_dirs.push(frontDir);
  }

  return FrontModelDirSchema.parse({
    model_type: modelDir.model_type,
    default_dir: modelDir.default_dir,
    dirs: front_dirs,
  });
}

export const ModelDownloadingInfoSchema = z.object({
  url: z.string(),
  model_info: ModelInfoSchema,
  total_size: z.number(),
  downloaded_size: z.number(),
  downloaded_time: z.number(),

  progress: z.number(),
  eta: z.number().optional().nullable(),

  finished: z.boolean(),
});

export type ModelDownloadingInfoType = z.infer<
  typeof ModelDownloadingInfoSchema
>;

export const ModelDownloadingInfoArraySchema = z.array(
  ModelDownloadingInfoSchema,
);

export type ModelDownloadingInfoArrayType = z.infer<
  typeof ModelDownloadingInfoArraySchema
>;
export const ModelInfoListSchema = z.array(ModelInfoSchema);
export type ModelInfoListType = z.infer<typeof ModelInfoListSchema>;
