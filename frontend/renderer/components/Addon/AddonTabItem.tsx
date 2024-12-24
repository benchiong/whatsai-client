import { AddonType } from "../../data-type/addons";
import { MantineColorsTuple } from "@mantine/core/lib/core/MantineProvider/theme.types";
import { Center, Group, Stack, Text, useMantineTheme } from "@mantine/core";
import React, { useCallback } from "react";
import {
  CompWidgetsType,
  SelectedSwitchableItemsType,
} from "../../data-type/widget";

export function AddonTabItem({
  addon,
  addonIndex,
  bg,
  selected,
  onClick,
}: {
  addon: AddonType;
  addonIndex: number;
  bg: string;
  selected: boolean;
  onClick: (idx: number) => void;
}) {
  const theme = useMantineTheme();
  const borderCss = selected
    ? "1px solid var(--mantine-color-waLight-8)"
    : "none";

  const getAddonNumber = useCallback(() => {
    if (addon.can_turn_off) {
      return addon.is_off ? 0 : 1;
    }

    if (addon.is_switchable) {
      const addonWidgetsArray = addon.widgets;
      const addonWidgets =
        addonWidgetsArray.length > 0 ? addonWidgetsArray[0] : null;
      if (!addonWidgets) {
        return 0;
      }
      const widgetsInfo = addonWidgets.length > 0 ? addonWidgets[0] : null;
      if (!widgetsInfo) {
        return 0;
      }

      return isSwitchableAddonEffective(
        widgetsInfo.value as SelectedSwitchableItemsType,
      );
    }

    // addon.is_off is undefined, the addon is comp list type(may have not only widgets)
    const addonWidgetsArray = addon.widgets;
    let addonNum = 0;
    for (let addonWidgets of addonWidgetsArray) {
      const effective = isAddonEffective(addonWidgets);
      if (effective) {
        addonNum += 1;
      }
    }
    return addonNum;
  }, [addon]);

  const isAddonEffective = useCallback((widgets: CompWidgetsType) => {
    let effective = true;
    for (const widget of widgets) {
      if (widget.value === null) {
        effective = false;
      }
    }
    return effective;
  }, []);

  const isSwitchableAddonEffective = useCallback(
    (items: SelectedSwitchableItemsType) => {
      for (const key in items) {
        if (items[key].selected) {
          return true;
        }
      }
      return false;
    },
    [],
  );

  return (
    <Stack
      gap={2}
      style={{
        position: "relative",
      }}
    >
      <Center
        key={addon.display_name}
        h={30}
        style={{
          cursor: "pointer",
          userSelect: "none",
          border: borderCss,
          backgroundColor: bg,
        }}
        onClick={() => onClick(addonIndex)}
      >
        <Text
          c={selected ? theme.white : theme.colors.waDark[0]}
          style={{
            fontSize: "10px",
          }}
          fw={selected ? 500 : 400}
        >
          {addon.display_name}
        </Text>
      </Center>
      <AddonItemNumberPanel num={getAddonNumber()} />
    </Stack>
  );
}

function AddonItemNumberPanel({ num }: { num: number }) {
  const theme = useMantineTheme();
  return (
    <Group
      justify={"center"}
      w={"100%"}
      h={3}
      bg={theme.colors.waLight[1]}
      gap={5}
      px={5}
    >
      {Array.from({ length: num }, (_, index) => (
        <AddonItemNumberPanelDot key={index} />
      ))}
    </Group>
  );
}

function AddonItemNumberPanelDot() {
  const theme = useMantineTheme();

  return (
    <Center
      style={{
        borderRadius: "3px",
      }}
      bg={theme.colors.primary[3]}
      flex={1}
      h={2}
    />
  );
}
