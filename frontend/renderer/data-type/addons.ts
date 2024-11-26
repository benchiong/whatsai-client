import { ModelInfoSchema } from "./model";
import { z } from "zod";
import { CompWidgetsSchema, WidgetsSchema } from "./widget";

export const LoraSchema = z.object({
  model: ModelInfoSchema.nullable(),
  weight: z.number(),
});

export type LoraType = z.infer<typeof LoraSchema>;

export const LoraAddonSchema = z.array(LoraSchema);
export type LoraAddonType = z.infer<typeof LoraAddonSchema>;

export const HypernetSchema = z.object({
  model: ModelInfoSchema.nullable(),
  strength: z.number(),
});

export type HypernetType = z.infer<typeof HypernetSchema>;

export const HypernetAddonSchema = z.array(HypernetSchema);
export type HypernetAddonType = z.infer<typeof HypernetAddonSchema>;

export const HiresFixSchema = z.object({
  activate: z.boolean(),
  widgetsInfo: WidgetsSchema,
});

export type HiresFixType = z.infer<typeof HiresFixSchema>;

export const UpscaleSchema = z.object({
  model: ModelInfoSchema.nullable(),
});

export type UpscaleType = z.infer<typeof UpscaleSchema>;

export const ControlnetSchema = z.object({
  model: ModelInfoSchema.nullable(),
  strength: z.number(),
  imagePath: z.string().nullable(),
});

export type ControlnetType = z.infer<typeof ControlnetSchema>;

export const ControlnetAddonSchema = z.array(ControlnetSchema);
export type ControlnetAddonType = z.infer<typeof ControlnetAddonSchema>;
export const AddonInfoSchema = z.object({
  LoRA: LoraAddonSchema.optional(),
  Hypernet: HypernetAddonSchema.optional(),
  HiresFix: HiresFixSchema.optional(),
  Upscale: UpscaleSchema.optional(),
  Controlnet: ControlnetAddonSchema.optional(),
});

export const AddonNameSchema = z.enum([
  "LoRA",
  "Hypernet",
  "HiresFix",
  "Upscale",
  "Controlnet",
]);
export type AddonNameType = z.infer<typeof AddonNameSchema>;

export const AddonWidgetsSchema = z.array(CompWidgetsSchema);
export type AddonWidgetsType = z.infer<typeof AddonWidgetsSchema>;
export const AddonSchema = z.object({
  addon_name: z.string(),
  display_name: z.string(),
  comp_list: z.boolean(),
  can_turn_off: z.boolean(),
  is_off: z.boolean().optional(),
  comp_widgets: CompWidgetsSchema, // use this to render new addon comp if it is comp list
  widgets: AddonWidgetsSchema, // use this to get user's inputs
});

export type AddonType = z.infer<typeof AddonSchema>;
