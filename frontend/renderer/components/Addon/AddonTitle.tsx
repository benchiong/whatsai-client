import { Text, useMantineTheme } from "@mantine/core";
import React from "react";

export function AddonTitle({ text }: { text: string }) {
  const theme = useMantineTheme();
  return (
    <Text
      w={"100%"}
      c={theme.colors.waDark[3]}
      style={{
        textAlign: "center",
        fontSize: "14px",
        fontWeight: 300,
        height: "40px",
        lineHeight: "40px",
        backgroundColor: "var(--mantine-color-waLight-4)",
        position: "sticky",
        top: "0px",
        zIndex: 420,
      }}
    >
      {text}
    </Text>
  );
}
