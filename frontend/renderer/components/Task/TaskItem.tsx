import { TaskType } from "../../data-type/task";
import { Stack, Image, Center, useMantineTheme } from "@mantine/core";
import { ImageLocal } from "../Image/ImageLocal";
import { TaskStatus } from "./TaskStatus";
import { IconX } from "@tabler/icons-react";
import { useState } from "react";
import { removeTask } from "../../lib/api";
import { useTasksContext } from "../../providers/TasksProvider";

export function TaskItem({ task }: { task: TaskType }) {
  const theme = useMantineTheme();

  const taskContext = useTasksContext();

  const images = task.outputs?.result.images;
  const imagesExist = !!(images && images[images.length - 1]);
  const [closeVisible, setCloseVisible] = useState(false);

  return (
    <Stack
      bg={theme.colors.waLight[1]}
      w={180}
      h={240}
      style={{
        position: "relative",
      }}
      align={"center"}
      onMouseEnter={() => setCloseVisible(true)}
      onMouseLeave={() => setCloseVisible(false)}
    >
      <TaskStatus task={task} />

      {closeVisible && (
        <Center
          style={{
            right: "0px",
            position: "absolute",
            width: "25px",
            height: "25px",
          }}
          onClick={(e) => {
            e.stopPropagation();
            if (!task.id) {
              return;
            }
            removeTask(task.id).then((r) => {
              taskContext.startLoop();
            });
          }}
        >
          <IconX
            style={{
              color: "var(--mantine-color-waLight-9)",
              cursor: "pointer",
              height: `20px`,
              width: `20px`,
              strokeWidth: "1px",
            }}
          />
        </Center>
      )}

      {task.preview_info?.preview_bytes && (
        <Center
          bg={theme.colors.waLight[1]}
          style={{
            borderRadius: "5px",
            overflow: "hidden",
          }}
          w={180}
          h={240}
        >
          <Image
            src={task.preview_info?.preview_bytes}
            w={180}
            h={240}
            style={{
              objectFit: "contain",
              borderRadius: "5px",
            }}
          />
        </Center>
      )}

      {!task.preview_info?.preview_bytes && images && (
        <Center
          bg={theme.colors.waLight[1]}
          style={{
            borderRadius: "5px",
            overflow: "hidden",
          }}
          w={180}
          h={240}
        >
          {imagesExist && (
            <ImageLocal
              localPath={images[images.length - 1].file_path}
              width={180}
              height={240}
              objectFit={"contain"}
            />
          )}
        </Center>
      )}
    </Stack>
  );
}
