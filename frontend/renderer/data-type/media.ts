import { z } from "zod";

export const MediaSchema = z.object({
  file_name: z.string(),
  file_path: z.string(),
  mime: z.string(),
  media_type: z.string(),
  sub_key: z.string(),
});

export type MediaType = z.infer<typeof MediaSchema>;

export const MediaArraySchema = z.array(MediaSchema);
export type MediaArrayType = z.infer<typeof MediaArraySchema>;
