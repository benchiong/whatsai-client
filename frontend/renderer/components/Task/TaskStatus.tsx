import { Center, Progress, Stack, useMantineTheme } from "@mantine/core";
import { TaskType } from "../../data-type/task";

// TaskStatus:
// queued = 1
// processing = 2
// canceled = 3
// failed = 4
// finished = 5

export function TaskStatus({ task }: { task: TaskType }) {
  const theme = useMantineTheme();

  const isQueued = task.status === "queued";
  const isProcessing = task.status === "processing";
  const isModelLoading = isProcessing && !task.preview_info;
  const isCanceled = task.status === "canceled";
  const isFailed = task.status === "failed";
  const isFinished = task.status === "done";

  let bgColor = theme.colors.waLight[3];
  let text;
  if (isQueued) {
    bgColor = "green.5";
    text = "Queued";
  }
  if (isProcessing) {
    bgColor = "green.5";
    text = "Processing";
  }
  if (isCanceled) {
    bgColor = "grey.5";
    text = "Processing";
  }
  if (isModelLoading) {
    bgColor = "orange.5";
    text = "Model Loading...";
  }

  if (isFailed) {
    bgColor = "red.5";
    text = "Failed";
  }

  if (isFinished) {
    bgColor = "green.5";
    text = "Finished";
  }

  const statusVisible = isQueued || isFailed || isModelLoading;
  const progressVisible = isProcessing && !isModelLoading;

  const taskProgress = task.preview_info
    ? (task.preview_info.step / task.preview_info.total_steps) * 100
    : 0;

  return (
    <Stack
      style={{
        position: "absolute",
        top: "0px",
        left: "0px",
        zIndex: 600,
      }}
      h={10}
      w={180}
    >
      {statusVisible && (
        <Center
          bg={bgColor}
          c={theme.white}
          h={16}
          w={isModelLoading ? 120 : 60}
          style={{
            fontSize: "12px",
            fontWeight: 500,
            zIndex: 200,
            borderRadius: "3px",
            position: "absolute",
            top: "0px",
          }}
        >
          {text}
        </Center>
      )}
      {progressVisible && (
        <Progress
          w={"100%"}
          radius={"none"}
          value={taskProgress}
          color={"green.4"}
          mb={-4}
          h={4}
          style={{
            zIndex: 601,
          }}
        />
      )}
    </Stack>
  );
}
