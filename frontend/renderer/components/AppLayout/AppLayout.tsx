import React from "react";
import { AppHeader } from "./AppHeader";
import { Flex, Group, ScrollArea } from "@mantine/core";
import { TaskDrawer } from "../Task/TaskDrawer";
import { NAV_WIDTH, TASK_DRAWER_WIDTH } from "../../extras/constants";
import { useTasksContext } from "../../providers/TasksProvider";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const taskContext = useTasksContext();
  const bodyWidth = taskContext.drawerOpened
    ? `calc(100vw - ${NAV_WIDTH}px - ${TASK_DRAWER_WIDTH}px)`
    : `calc(100vw - ${NAV_WIDTH}px`;

  return (
    <Flex h={"100vh"} style={{ position: "relative" }} direction="row">
      <AppHeader />
      <Group
        align={"start"}
        w={bodyWidth}
        style={{ transition: "width 0.3s ease" }}
      >
        <ScrollArea
          w={"100%"}
          h={"100%"}
          style={{ transition: "height 0.3s ease" }}
          scrollbars="y"
          scrollbarSize={2}
        >
          {children}
        </ScrollArea>
      </Group>
      <TaskDrawer />
    </Flex>
  );
}
