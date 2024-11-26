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

export const WorkFlowSchema = z.array(CardInfoSchema);
export type WorkFlowType = z.infer<typeof WorkFlowSchema>;

export const SimpleCardInfoSchema = z.object({
  card_name: z.string(),
  describe: z.string().nullable(),
  card_type: z.string(),
  location: z.string().nullable(),
  remote_url: z.string().nullable(),
  pre_models: z.array(z.string()),
  cover_image: z.string().nullable(),
  is_ready: z.boolean(),
});

export type SimpleCardInfoType = z.infer<typeof SimpleCardInfoSchema>;

export const SimpleCardInfoArraySchema = z.array(SimpleCardInfoSchema);
export type SimpleCardInfoArrayType = z.infer<typeof SimpleCardInfoArraySchema>;
