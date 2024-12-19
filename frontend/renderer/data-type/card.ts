import { z } from "zod";
import { WidgetUnionsSchema } from "./widget";
import { AddonSchema } from "./addons";

export const AddonListSchema = z.array(AddonSchema);
export type AddonListType = z.infer<typeof AddonListSchema>;

export const CardInfoSchema = z.object({
  card_name: z.string(),
  card_display_name: z.string().nullable().optional(),
  widgets: z.array(WidgetUnionsSchema),
  addons: AddonListSchema,
});

export type CardInfoType = z.infer<typeof CardInfoSchema>;

export const PreModelSchema = z.object({
  hash: z.string().optional().nullable(),
  download_url: z.string().optional().nullable(),
  file_name: z.string().optional().nullable(),
});

export type PreModelType = z.infer<typeof PreModelSchema>;

export const SimpleCardInfoSchema = z.object({
  id: z.number(),
  card_name: z.string(),
  display_name: z.string().nullable(),
  describe: z.string().nullable(),
  card_type: z.string(),
  location: z.string().nullable(),
  remote_url: z.string().nullable(),
  pre_models: z.array(PreModelSchema),
  cover_image: z.string().nullable(),
});

export type SimpleCardInfoType = z.infer<typeof SimpleCardInfoSchema>;

export const SimpleCardInfoArraySchema = z.array(SimpleCardInfoSchema);
export type SimpleCardInfoArrayType = z.infer<typeof SimpleCardInfoArraySchema>;
