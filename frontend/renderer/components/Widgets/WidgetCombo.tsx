import { Group, Select } from "@mantine/core";
import { useEffect, useState } from "react";
import { LabelName } from "./LabelName";

export function WidgetCombo({
  text,
  values,
  onChange,
  defaultValue = "euler",
  width = "100%",
  height = 36,
}: {
  text: string;
  values: string[];
  defaultValue: string;
  onChange?: (value: string) => void;
  width?: number | string;
  height?: number;
}) {
  const [value, setValue] = useState<string>(defaultValue);
  useEffect(() => {
    setValue(defaultValue);
  }, [defaultValue]);

  return (
    <Group
      justify={"center"}
      w={width}
      pl={10}
      style={{
        borderRadius: 20,
        border: "1px solid var(--mantine-color-waLight-3)",
        backgroundColor: "var(--mantine-color-waLight-3)",
      }}
    >
      <LabelName text={text} />

      <Select
        value={value}
        flex={1}
        data={values}
        searchable
        styles={{
          dropdown: {
            borderRadius: "5px",
          },
          input: {
            height: `${height}px`,
            border: "none",
            textAlign: "center",
            backgroundColor: "var(--mantine-color-waLight-4)",
          },
        }}
        rightSectionProps={{
          color: "var(--mantine-color-primary-9)",
        }}
        defaultValue={defaultValue}
        onChange={(_value, _) => {
          onChange && onChange(_value ?? "");
          setValue(_value ?? "");
        }}
      />
    </Group>
  );
}
