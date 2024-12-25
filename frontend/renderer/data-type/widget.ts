import { z } from "zod";

const WidgetTypeEnumSchema = z.enum([
  "BoolWidget",
  "IntWidget",
  "TextWidget",
  "SeedWidget",
  "FloatWidget",
  "ComboWidget",
  "ModelComboWidget",
  "FileWidget",
  "ImageWidget",
  "VideoWidget",
  "AudioWidget",
  "SwitchableWidgets",
  "GroupedWidgets",
]);
export type WidgetTypeEnumType = z.infer<typeof WidgetTypeEnumSchema>;

export const WidgetSchema = z.object({
  param_name: z.string().optional(),
  display_name: z.string(),
  widget_type: WidgetTypeEnumSchema,
  optional: z.boolean().optional(),
  visible: z.boolean().optional().nullable(),
});

export type WidgetType = z.infer<typeof WidgetSchema>;

export const WidgetBoolSchema = WidgetSchema.extend({
  value: z.boolean(),
});

export type WidgetBoolType = z.infer<typeof WidgetBoolSchema>;

export const WidgetIntSchema = WidgetSchema.extend({
  value: z.number(),
  min: z.number(),
  max: z.number(),
  step: z.number(),
});

export type WidgetIntType = z.infer<typeof WidgetIntSchema>;

export const WidgetFloatSchema = WidgetSchema.extend({
  round: z.number(),
  value: z.number(),
  min: z.number(),
  max: z.number(),
  step: z.number(),
});

export type WidgetFloatType = z.infer<typeof WidgetFloatSchema>;

export const WidgetTextSchema = WidgetSchema.extend({
  value: z.string(),
});

export type WidgetTextType = z.infer<typeof WidgetTextSchema>;

export const WidgetSeedSchema = WidgetSchema.extend({
  max: z.number(),
  value: z.number(),
});

export type WidgetSeedType = z.infer<typeof WidgetSeedSchema>;

export const WidgetComboSchema = WidgetSchema.extend({
  value: z.string(),
  values: z.string().array(),
});

export type WidgetComboType = z.infer<typeof WidgetComboSchema>;

export const WidgetModelComboSchema = WidgetSchema.extend({
  values_function_name: z.string(),
  values_function_params: z.any().nullable(),
  value: z.string().nullable(),
});

export type WidgetModelComboType = z.infer<typeof WidgetModelComboSchema>;

export const WidgetImageSchema = WidgetSchema.extend({
  value: z.string().nullable(),
});
export type WidgetImageType = z.infer<typeof WidgetImageSchema>;

export const WidgetUnionsWithoutGroupSchema = z.union([
  WidgetModelComboSchema,
  WidgetComboSchema, // the position matters, don't know why.
  WidgetBoolSchema,
  WidgetIntSchema,
  WidgetTextSchema,
  WidgetSeedSchema,
  WidgetFloatSchema,
  WidgetImageSchema,
]);
export type WidgetUnionsWithoutGroupType = z.infer<
  typeof WidgetUnionsWithoutGroupSchema
>;

export const WidgetsWithoutGroupSchema = z.array(
  WidgetUnionsWithoutGroupSchema,
);
export type WidgetsWithoutGroupType = z.infer<typeof WidgetsWithoutGroupSchema>;

export const SwitchableItemsSchema = z.record(WidgetsWithoutGroupSchema);
export type SwitchableItemsType = z.infer<typeof SwitchableItemsSchema>;

export const SingleSelectedSwitchableItemSchema = z.object({
  selected: z.boolean(),
  widgets: WidgetsWithoutGroupSchema,
});
export const SingleSelectedSwitchableItemType = z.infer<
  typeof SingleSelectedSwitchableItemSchema
>;

export const SelectedSwitchableItemsSchema = z.record(
  SingleSelectedSwitchableItemSchema,
);
export type SelectedSwitchableItemsType = z.infer<
  typeof SelectedSwitchableItemsSchema
>;

export const SwitchableWidgetsSchema = WidgetSchema.extend({
  value: SelectedSwitchableItemsSchema,
  values: SwitchableItemsSchema,
});
export type SwitchableWidgetsType = z.infer<typeof SwitchableWidgetsSchema>;

export const GroupedWidgetsSchema = WidgetSchema.extend({
  value: z.array(WidgetUnionsWithoutGroupSchema),
});
export type GroupedWidgetsType = z.infer<typeof GroupedWidgetsSchema>;

export const WidgetUnionsSchema = z.union([
  GroupedWidgetsSchema,
  SwitchableWidgetsSchema,
  WidgetModelComboSchema,
  WidgetComboSchema,
  WidgetBoolSchema,
  WidgetIntSchema,
  WidgetTextSchema,
  WidgetSeedSchema,
  WidgetFloatSchema,
  WidgetImageSchema,
]);
export type WidgetUnionsType = z.infer<typeof WidgetUnionsSchema>;

export const WidgetsSchema = z.array(WidgetUnionsSchema);
export type WidgetsType = z.infer<typeof WidgetsSchema>;

export const CompWidgetsSchema = z.array(WidgetUnionsSchema);
export type CompWidgetsType = z.infer<typeof CompWidgetsSchema>;
