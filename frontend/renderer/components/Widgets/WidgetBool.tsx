import { Flex, Group, Switch, useMantineTheme } from "@mantine/core";
import { LabelName } from "./LabelName";

export function WidgetBool({
  text,
  value,
  onChange,
  width = "100%",
  height = 38,
}: {
  text: string;
  value: boolean;
  width?: number | string;
  height?: number;
  onChange?: (value: boolean) => void;
}) {
  const theme = useMantineTheme();

  return (
    <Group
      justify={"center"}
      style={{
        borderRadius: `${height}px`,
        cursor: "pointer",
      }}
      bg={theme.colors.waLight[3]}
      px={10}
      w={width}
      miw={220}
      h={height}
    >
      <Group
        flex={1}
        h={height}
        style={{
          borderRadius: "30px",
          cursor: "pointer",
        }}
        justify={"space-between"}
      >
        <Flex justify={"space-between"} align={"center"} w={"100%"}>
          <LabelName text={text} />

          <Switch
            size="sm"
            onLabel="ON"
            offLabel="OFF"
            checked={value}
            onChange={(event) => {
              const newValue = event.currentTarget.checked;
              onChange(newValue);
            }}
          />
        </Flex>
      </Group>
    </Group>
  );
}
