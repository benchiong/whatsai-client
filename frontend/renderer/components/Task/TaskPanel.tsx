import { ScrollArea, Stack } from "@mantine/core";
import React from "react";
import { useTasksContext } from "../../providers/TasksProvider";
import { TaskItem } from "./TaskItem";

export function TaskPanel({ height }: { height: string }) {
  const tasksContext = useTasksContext();
  const tasks = tasksContext.tasks;

  return (
    <ScrollArea
      h={height}
      style={{ transition: "height 0.3s ease" }}
      scrollbars="y"
      scrollbarSize={2}
      py={20}
    >
      <Stack align={"center"} gap={20}>
        {tasks.map((task) => {
          return <TaskItem task={task} key={task.id} />;
        })}
      </Stack>
    </ScrollArea>
  );
}
