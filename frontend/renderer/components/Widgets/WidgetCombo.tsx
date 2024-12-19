import { Group, Select } from "@mantine/core";
import { LabelName } from "./LabelName";

export function WidgetCombo({
  text,
  values,
  onChange,
  value = "euler",
  width = "100%",
  height = 36,
}: {
  text: string;
  values: string[];
  value: string;
  onChange?: (value: string) => void;
  width?: number | string;
  height?: number;
}) {
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
        defaultValue={value}
        onChange={(_value, _) => {
          onChange && onChange(_value ?? "");
        }}
      />
    </Group>
  );
}
