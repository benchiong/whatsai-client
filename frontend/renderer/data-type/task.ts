import { z } from "zod";
import { ArtworkSchema } from "./artwork";

// TaskStatus:
// queued = 1
// processing = 2
// canceled = 3
// failed = 4
// finished = 5

export const TaskStatusSchema = z.enum([
  "queued",
  "processing",
  "canceled",
  "failed",
  "finished",
  "unknown",
]);

export type TaskStatusType = z.infer<typeof TaskStatusSchema>;

export function taskNum2Status(num: number) {
  switch (num) {
    case 1:
      return TaskStatusSchema.Enum.queued;
    case 2:
      return TaskStatusSchema.Enum.processing;
    case 3:
      return TaskStatusSchema.Enum.canceled;
    case 4:
      return TaskStatusSchema.Enum.failed;
    case 5:
      return TaskStatusSchema.Enum.finished;
    default:
      return TaskStatusSchema.Enum.unknown;
  }
}

export const TaskSchema = z.object({
  id: z.number().nullable(),
  client_id: z.string(),
  status: z.string(),
  prompt: z.object({
    card_name: z.string(),
    base_inputs: z.any(),
    addon_inputs: z.any(),
  }),
  outputs: z
    .object({
      result: z.object({
        images: z.array(ArtworkSchema).optional(),
      }),
    })
    .nullable(),

  preview_info: z
    .object({
      step: z.number(),
      total_steps: z.number(),
      preview_bytes: z.string(),
    })
    .nullable(),

  created_time_stamp: z.number(),
  created_datetime_str: z.string(),
  info: z.string().nullable(),
});

export type TaskType = z.infer<typeof TaskSchema>;

export const TaskArraySchema = z.array(TaskSchema);
export type TaskArrayType = z.infer<typeof TaskArraySchema>;
