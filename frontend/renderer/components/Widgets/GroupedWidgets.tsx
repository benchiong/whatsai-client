import { WidgetsType } from "../../data-type/widget";
import { WidgetsRender } from "./WidgetsRender";
import React, { useEffect, useState } from "react";
import { Collapse, Stack, Group, useMantineTheme, Title } from "@mantine/core";
import {
  IconLayoutNavbarCollapse,
  IconLayoutBottombarCollapse,
} from "@tabler/icons-react";
import { useLocalStorage } from "@mantine/hooks";
import { useCardContext } from "../../providers/CardProvider";

export function GroupedWidgets({
  text,
  widgets,
  onChange,
  width = "100%",
}: {
  text: string;
  widgets: WidgetsType;
  onChange: (value: WidgetsType) => void;
  width: number | string;
}) {
  const theme = useMantineTheme();

  const cardContext = useCardContext();

  const [collapsed, setCollapsed] = useLocalStorage({
    key: `${cardContext.cardName}-${text}`,
    defaultValue: widgets.length > 2,
  });

  return (
    <Stack
      justify={"start"}
      style={{
        borderRadius: `10px`,
        cursor: "pointer",
        position: "relative",
      }}
      w={width}
      miw={220}
      bg={theme.colors.waLight[2]}
      pb={!collapsed ? 20 : 10}
      gap={!collapsed ? 20 : 0}
    >
      <Group
        justify={"space-between"}
        align={"center"}
        w={"100%"}
        mt={10}
        pr={10}
      >
        <Title
          order={5}
          h={20}
          c={theme.colors.waDark[9]}
          mx={15}
          style={{
            textAlign: "start",
            userSelect: "none",
            lineHeight: "20px",
            fontSize: "14px",
            fontWeight: "400",
          }}
        >
          {text}
        </Title>
        {!collapsed ? (
          <IconLayoutNavbarCollapse
            style={{
              color: "var(--mantine-color-waDark-8)",
              cursor: "pointer",
              height: "22px",
              width: "22px",
              strokeWidth: "1px",
            }}
            onClick={(event) => {
              setCollapsed(!collapsed);
            }}
          />
        ) : (
          <IconLayoutBottombarCollapse
            style={{
              color: "var(--mantine-color-primary-3)",
              cursor: "pointer",
              height: "22px",
              width: "22px",
              strokeWidth: "1px",
            }}
            onClick={(event) => {
              setCollapsed(!collapsed);
            }}
          />
        )}
      </Group>
      <Stack align={"center"} m={0} p={0}>
        <Collapse in={!collapsed} transitionDuration={100}>
          <WidgetsRender
            width={420}
            widgets={widgets}
            onChange={(widgets) => {
              onChange(widgets);
            }}
          />
        </Collapse>
      </Stack>
    </Stack>
  );
}
