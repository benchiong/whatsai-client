import {
  SelectedSwitchableItemsType,
  SingleSelectedSwitchableItemType,
  SwitchableItemsType,
} from "../../data-type/widget";
import {
  Center,
  Chip,
  Group,
  Stack,
  Text,
  Title,
  useMantineTheme,
} from "@mantine/core";
import React, { useCallback, useEffect, useState } from "react";
import { WidgetsRender } from "./WidgetsRender";

export function SwitchableWidgets({
  text,
  values,
  value,
  onChange,
  width = "100%",
}: {
  text: string;
  values: SwitchableItemsType;
  value: SelectedSwitchableItemsType;
  onChange: (value: SelectedSwitchableItemsType) => void;
  width: number | string;
}) {
  if (!value) {
    return <></>;
  }

  const theme = useMantineTheme();
  const keys = value ? Object.keys(value) : [];
  const [selectedKey, setSelectedKey] = useState<string>(keys[0]); // tab selection
  const [on, SetOn] = useState<string | null>(null); // which one is on

  const selectedValue: SingleSelectedSwitchableItemType = value[selectedKey];

  const whichOneIsOn = useCallback((items: SelectedSwitchableItemsType) => {
    for (const key in items) {
      if (items[key].selected) {
        return key;
      }
    }
    return null;
  }, []);

  useEffect(() => {
    const isOn = whichOneIsOn(value);
    SetOn(isOn);
    setSelectedKey(isOn ? isOn : keys[0]);
  }, [value]);

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
      pb={20}
      gap={0}
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
        <Stack>
          <Group justify={"center"} bg={theme.colors.waLight[3]}>
            {keys.map((key) => {
              return (
                <TabItem
                  key={key}
                  name={key}
                  selected={selectedKey == key}
                  isOn={on == key}
                  onClick={(selectedName) => {
                    setSelectedKey(selectedName);
                  }}
                />
              );
            })}
          </Group>
          <Stack align={"center"} mx={15}>
            <Chip
              size={"xs"}
              key={selectedKey}
              checked={selectedValue.selected}
              onChange={() => {
                const newValue: SelectedSwitchableItemsType = { ...value };
                const newSelectedValue = { ...selectedValue };
                newSelectedValue["selected"] = !selectedValue.selected;
                if (!selectedValue.selected) {
                  for (let key in newValue) {
                    if (key !== selectedKey) {
                      newValue[key].selected = false;
                    }
                  }
                }
                newValue[selectedKey] = { ...newSelectedValue };
                onChange(newValue);
              }}
            >
              {!selectedValue.selected
                ? `Use ${selectedKey}`
                : `Unselect ${selectedKey}`}
            </Chip>
            <WidgetsRender
              width={"100%"}
              widgets={selectedValue.widgets}
              onChange={(changedWidgets) => {
                const newValue: SelectedSwitchableItemsType = { ...value };
                const newSelectedValue = { ...selectedValue };
                newSelectedValue["widgets"] = changedWidgets;
                newValue[selectedKey] = { ...newSelectedValue };
                onChange(newValue);
              }}
            />
          </Stack>
        </Stack>
      </Group>
    </Stack>
  );
}

function TabItem({
  name,
  selected,
  isOn,
  onClick,
}: {
  name: string;
  selected: boolean;
  isOn: boolean;
  onClick: (name: string) => void;
}) {
  const theme = useMantineTheme();
  const bg = selected
    ? "var(--mantine-color-waLight-1)"
    : "var(--mantine-color-waLight-3)";

  return (
    <Stack style={{ position: "relative" }} align={"center"}>
      <Center
        key={name}
        h={30}
        mx={5}
        style={{
          cursor: "pointer",
          userSelect: "none",
          backgroundColor: bg,
        }}
        onClick={() => onClick(name)}
      >
        <Text
          c={theme.colors.waDark[0]}
          px={10}
          style={{
            fontSize: "12px",
          }}
          fw={300}
        >
          {name}
        </Text>
      </Center>
      {isOn && (
        <Center
          style={{
            position: "absolute",
            borderRadius: "2px",
            width: "85%",
            bottom: "0px",
          }}
          bg={theme.colors.primary[3]}
          flex={1}
          h={2}
        />
      )}
    </Stack>
  );
}
