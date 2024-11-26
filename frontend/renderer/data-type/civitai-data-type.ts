import { z } from "zod";

// civitai urls:
// https://civitai.com/api/v1/model-versions/by-hash/A5E5A941A3217247DBCECEEE5B67F8D6B1EF2514260E08A5757436BEC7035F93
// https://civitai.com/api/v1/models/7240
// https://civitai.com/api/v1/model-versions/948574

export const CivitaiFileHashesSchema = z.object({
  AutoV1: z.string().optional().nullable(),
  AutoV2: z.string().optional().nullable(),
  SHA256: z.string().optional().nullable(),
  CRC32: z.string().optional().nullable(),
  BLAKE3: z.string().optional().nullable(),
  AutoV3: z.string().optional().nullable(),
});

export type CivitaiFileHashesType = z.infer<typeof CivitaiFileHashesSchema>;

export const CivitaiFileSchema = z.object({
  id: z.number(),
  sizeKB: z.number(),
  name: z.string(),
  type: z.string(),
  hashes: CivitaiFileHashesSchema,
  primary: z.boolean().optional(),
  downloadUrl: z.string(),
});

export type CivitaiFileType = z.infer<typeof CivitaiFileSchema>;

export const CivitaiFileArraySchema = z.array(CivitaiFileSchema);
export type CivitaiFileArrayType = z.infer<typeof CivitaiFileArraySchema>;

export const CivitaiFileToDownloadSchema = z.object({
  civitaiFile: CivitaiFileSchema,
  modelType: z.string().nullable(),
});

export type CivitaiFileToDownloadType = z.infer<
  typeof CivitaiFileToDownloadSchema
>;
export const CivitaiFileToDownLoadArraySchema = z.array(
  CivitaiFileToDownloadSchema,
);
export type CivitaiFileToDownLoadArrayType = z.infer<
  typeof CivitaiFileToDownLoadArraySchema
>;

export const CivitaiImageMetaDataSchema = z.object({
  hash: z.string().optional().nullable(),
  size: z.number().optional().nullable(),
  width: z.number().optional().nullable(),
  height: z.number().optional().nullable(),
});

export type CivitaiImageMetaDataType = z.infer<
  typeof CivitaiImageMetaDataSchema
>;

export const CivitaiImageSchema = z.object({
  url: z.string().optional().nullable(),
  nsfwLevel: z.number().optional().nullable(),
  width: z.number().optional().nullable(),
  height: z.number().optional().nullable(),
  hash: z.string().optional().nullable(),
  type: z.string().optional().nullable(),

  metadata: CivitaiImageMetaDataSchema.optional().nullable(),
});

export type CivitaiImageType = z.infer<typeof CivitaiImageSchema>;

export const CivitaiModelVersionModelSchema = z.object({
  name: z.string().optional().nullable(),
  type: z.string().optional().nullable(),
  nsfw: z.boolean().optional().nullable(),
  poi: z.boolean().optional().nullable(),
});

export type CivitaiModelVersionModelType = z.infer<
  typeof CivitaiModelVersionModelSchema
>;

// Version info lack of info of model, so CivitAI add this field to make it complete.
export const CivitaiModelInfoOfVersionSchema = z.object({
  name: z.string().optional().nullable(),
  type: z.string().optional().nullable(),
  nsfw: z.boolean().optional().nullable(),
  poi: z.boolean().optional().nullable(),
});

export type CivitaiModelInfoOfVersionType = z.infer<
  typeof CivitaiModelInfoOfVersionSchema
>;

export const CivitaiModelVersionSchema = z.object({
  id: z.number().nullable().optional(),
  modelId: z.number().nullable().optional(),
  name: z.string().optional(),
  baseModel: z.string().optional().nullable(),
  baseModelType: z.string().optional().nullable(),
  description: z.string().optional().nullable(),
  model: CivitaiModelInfoOfVersionSchema.optional().nullable(),

  files: CivitaiFileArraySchema,
  images: z.array(CivitaiImageSchema),

  downloadUrl: z.string(),
});

export type CivitaiModelVersionType = z.infer<typeof CivitaiModelVersionSchema>;

export const CivitaiModelSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable().optional(),
  type: z.string().nullable().optional(),
  nsfw: z.boolean().nullable().optional(),
  nsfwLevel: z.number().nullable().optional(),

  modelVersions: z.array(CivitaiModelVersionSchema),
});

export type CivitaiModelType = z.infer<typeof CivitaiModelSchema>;
