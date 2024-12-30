import { useEffect, useState } from "react";
import { Group, Select } from "@mantine/core";
import { getAllModelTypes } from "../../lib/api";
import { CivitaiFileToDownloadType } from "../../data-type/civitai-data-type";

export function ModelTypeSelector({
  onChange,
  width = "100%",
  height = 36,
  modelType = null,
}: {
  onChange?: (value: string) => void;
  width?: number | string;
  height?: number;
  modelType?: string | null;
}) {
  const [value, setValue] = useState<string | null>(modelType);
  const [values, setValues] = useState<string[]>([]);

  useEffect(() => {
    getAllModelTypes()
      .then((types) => {
        setValues(types);
      })
      .catch((e) => {});
  }, []);

  return (
    <Group
      justify={"center"}
      w={width}
      style={{
        borderRadius: 5,
      }}
    >
      <Select
        radius={5}
        value={value}
        data={values}
        flex={1}
        searchable
        styles={{
          dropdown: {
            borderRadius: "5px",
          },
          input: {
            width: "100%",
            height: `${height}px`,
            border: "none",
            textAlign: "center",
            backgroundColor: "var(--mantine-color-waLight-3)",
          },
        }}
        rightSectionProps={{
          color: "var(--mantine-color-primary-9)",
        }}
        defaultValue={value}
        onChange={(_value, _) => {
          onChange && onChange(_value ?? "");
          setValue(_value ?? "");
        }}
      />
    </Group>
  );
}
