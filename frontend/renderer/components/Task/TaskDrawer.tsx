import { IconChevronLeft, IconChevronRight } from "@tabler/icons-react";
import { Center, Drawer, useMantineTheme, Text } from "@mantine/core";
import { MouseEventHandler } from "react";
import { TASK_DRAWER_WIDTH } from "../../extras/constants";
import { useTasksContext } from "../../providers/TasksProvider";
import { TaskPanel } from "./TaskPanel";

export function TaskDrawer() {
  const tasksContext = useTasksContext();
  const theme = useMantineTheme();

  return (
    <>
      <FloatButton
        onClick={() => {
          tasksContext.toggleDrawerOpened();
        }}
      />

      <Drawer
        lockScroll={false}
        zIndex={299}
        opened={tasksContext.drawerOpened}
        position={"right"}
        onClose={() => tasksContext.setDrawerOpened(false)}
        withOverlay={false}
        shadow={"lg"}
        size={`${TASK_DRAWER_WIDTH}px`}
        withCloseButton={false}
        transitionProps={{ duration: 300, timingFunction: "const" }}
        styles={{
          content: {
            borderLeft: "1px solid var(--mantine-color-waLight-2)",
            backgroundColor: `var(--mantine-color-waLight-0)`,
          },
          body: {
            padding: "0px",
          },
        }}
      >
        <Center
          h={50}
          mr={16}
          bg={theme.colors.waLight[1]}
          style={{
            position: "relative",
          }}
        >
          <Text>Tasks</Text>

          {tasksContext.processingCount > 0 && (
            <Text
              span={true}
              ml={20}
              px={6}
              py={2}
              style={{
                backgroundColor: `var(--mantine-color-primary-2)`,
                borderRadius: "20px",
                fontSize: "14px",
                lineHeight: "14px",
                color: "#fff",
                fontWeight: 500,
                position: "absolute",
                left: "160px",
              }}
            >
              {tasksContext.processingCount}
            </Text>
          )}
        </Center>
        <TaskPanel height={`calc(100vh - 50px)`} />
      </Drawer>
    </>
  );
}

export function FloatButton({
  onClick,
}: {
  onClick: MouseEventHandler<HTMLDivElement> | undefined;
}) {
  const theme = useMantineTheme();
  const tasksContext = useTasksContext();

  return (
    <Center
      bg={theme.colors.waLight[1]}
      w={16}
      h={50}
      style={{
        position: "fixed",
        right: "0px",
        top: "0px",
        borderBottomLeftRadius: "5px",
        borderTopLeftRadius: "5px",
        zIndex: 600,
      }}
      onClick={onClick}
    >
      {tasksContext.drawerOpened ? (
        <IconChevronRight
          style={{
            color: "var(--mantine-color-primary-4)",
            cursor: "pointer",
            height: "16px",
            width: "16px",
          }}
        />
      ) : (
        <IconChevronLeft
          style={{
            color: "var(--mantine-color-primary-4)",
            cursor: "pointer",
            height: "16px",
            width: "16px",
          }}
        />
      )}
    </Center>
  );
}
