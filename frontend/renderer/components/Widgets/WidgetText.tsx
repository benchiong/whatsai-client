import { Stack, Textarea, Title, useMantineTheme } from "@mantine/core";
import { useEffect, useState } from "react";
import { LabelSingleLine } from "./LabelSingleLine";

export function WidgetText({
  text,
  value,
  onChange,
  width = "100%",
}: {
  text: string;
  value: string;
  onChange?: (value: string) => void;
  width?: number | string;
}) {
  const theme = useMantineTheme();
  return (
    <Stack
      justify={"start"}
      style={{
        borderRadius: `10px`,
        cursor: "pointer",
      }}
      w={width}
      miw={220}
      bg={theme.colors.waLight[3]}
    >
      <LabelSingleLine text={text} />

      <Textarea
        autosize
        radius={"sm"}
        value={value}
        minRows={3}
        maxRows={8}
        mb={15}
        mx={10}
        onChange={(e) => {
          const value = e.target.value;
          onChange && onChange(value);
        }}
        placeholder={`Enter ${text.toLowerCase()} here.`}
      ></Textarea>
    </Stack>
  );
}
