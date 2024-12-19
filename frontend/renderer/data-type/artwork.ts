import { z } from "zod";

export const PromptSchema = z.object({
  card_name: z.string(),
  base_inputs: z.any(),
  addon_inputs: z.any().nullable(),
});

export type PromptType = z.infer<typeof PromptSchema>;

export const ThumbImageSchema = z.object({
  file_path: z.string().nullable(),
  thumb_width: z.number().nullable(),
  thumb_height: z.any().nullable(),
});

export type ThumbImageType = z.infer<typeof ThumbImageSchema>;

export const ArtworkSchema = z.object({
  id: z.number(),
  file_path: z.string(),
  media_type: z.string(),
  meta_info: z.any(),

  liked: z.boolean(),
  shared: z.boolean(),

  card_name: z.string(),
  prompt: PromptSchema,

  thumb: ThumbImageSchema.nullable(),

  created_time_stamp: z.number(),
  created_datetime_str: z.string(),
});

export type ArtworkType = z.infer<typeof ArtworkSchema>;

export const ArtworkArraySchema = z.array(ArtworkSchema);
export type ArtworkArrayType = z.infer<typeof ArtworkArraySchema>;
