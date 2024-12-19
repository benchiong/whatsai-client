import { Group, Text, useMantineTheme } from "@mantine/core";
import React from "react";

export function ParamItem({ name, value }: { name: string; value: any }) {
  const theme = useMantineTheme();
  const isModel = typeof value === "object" && "file_name" in value;
  let displayStr: string;
  if (isModel) {
    displayStr = value["file_name"];
  } else {
    displayStr = value.toString();
  }

  return (
    <Group>
      <Text
        w={150}
        style={{
          textAlign: "right",
          fontSize: "14px",
          wordBreak: "break-all",
        }}
        lineClamp={2}
      >
        {name}:
      </Text>
      <Text
        ml={20}
        p={5}
        px={15}
        maw={400}
        bg={theme.colors.waLight[5]}
        style={{
          maxLines: 5,
          maxWidth: "400px",
          wordBreak: "break-all",
        }}
      >
        {displayStr}
      </Text>
    </Group>
  );
}
