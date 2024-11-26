import { z } from "zod";

export const ArtworkSchema = z.object({
  artwork_id: z.number().optional(),
  card_name: z.string(),
  path: z.string(),
  media_type: z.string(),
  meta_info: z.object({
    width: z.number().nullable(),
    height: z.number().nullable(),
  }),
  tags: z.array(z.string()).nullable(),
  liked: z.boolean(),
  shared: z.boolean(),
  inputs_info: z.any(),
  addon_inputs_info: z.any(),
  info: z.string().nullable(),
  thumb: z.string(),
  thumb_width: z.number(),
  thumb_height: z.number(),
  created_time_stamp: z.number(),
  created_datetime_str: z.string(),
});

export type ArtworkType = z.infer<typeof ArtworkSchema>;

export const ArtworkArraySchema = z.array(ArtworkSchema);
export type ArtworkArrayType = z.infer<typeof ArtworkArraySchema>;
