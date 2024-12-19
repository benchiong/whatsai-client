import { z } from "zod";
import { CompWidgetsSchema } from "./widget";

export const AddonWidgetsSchema = z.array(CompWidgetsSchema);
export type AddonWidgetsType = z.infer<typeof AddonWidgetsSchema>;
export const AddonSchema = z.object({
  addon_name: z.string(),
  display_name: z.string(),
  comp_list: z.boolean(),
  can_turn_off: z.boolean(),
  is_off: z.boolean().optional().nullable(),
  comp_widgets: CompWidgetsSchema, // use this to render new addon comp if it is comp list
  widgets: AddonWidgetsSchema, // use this to get user's inputs
});

export type AddonType = z.infer<typeof AddonSchema>;
