import {
  Group,
  Flex,
  Text,
  TextInput,
  Button,
  Popover,
  useMantineTheme,
} from "@mantine/core";
import { useState } from "react";
import { getHotkeyHandler, useClickOutside } from "@mantine/hooks";
import { ChevronLeft } from "./ChevronLeft";
import { ChevronRight } from "./ChevronRight";
import { LabelName } from "./LabelName";
import { showNormalNotification } from "../../utils/notifications";

export function WidgetInt({
  text,
  value,
  onChange,
  step = 1,
  max = 100,
  min = 0,
  width = "100%",
  height = 38,
}: {
  text: string;
  value: number;
  step: number;
  max: number;
  min: number;
  width?: number | string;
  height?: number;
  onChange?: (value: number) => void;
}) {
  const theme = useMantineTheme();
  const [inputValue, setInputValue] = useState<string>(value.toString());
  const [opened, setOpened] = useState<boolean>(false);
  const ref = useClickOutside(() => setOpened(false));

  const innerOnChange = (value: number) => {
    onChange && onChange(value);
  };
  const increase = () => {
    let newValue = value + step;
    newValue = Math.min(newValue, max);
    if (newValue > max) {
      showNormalNotification({
        title: "Reach the maximum value",
        message: `Value of ${text}: ${value} has reached the maximum.`,
      });
    }
    innerOnChange(newValue);
  };

  const decrease = () => {
    let newValue = value - step;
    newValue = Math.max(newValue, min);
    if (newValue < min) {
      showNormalNotification({
        title: "Reach the minimum value",
        message: `Value of ${text}: ${value} has reached the minimum.`,
      });
    }
    innerOnChange(newValue);
  };

  const popoverOKButtonOnClick = () => {
    setOpened(false);
    const intValue = parseInt(inputValue);
    if (isNaN(intValue)) {
      innerOnChange(value);
    } else {
      const value = Math.min(max, Math.max(min, intValue));
      innerOnChange(value);
    }
  };

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
      <Popover opened={opened} trapFocus position="bottom" shadow="md">
        <Popover.Target>
          <Group
            flex={1}
            h={height}
            style={{
              borderRadius: "30px",
              cursor: "pointer",
            }}
            justify={"space-between"}
            onClick={() => setOpened(true)}
          >
            <Flex justify={"space-between"} align={"center"} w={"100%"}>
              <LabelName text={text} />

              <Flex flex={1} w={"100%"} justify={"space-between"} ml={10}>
                <ChevronLeft onClick={decrease} disabled={value <= min} />

                <Text
                  style={{
                    fontSize: "14px",
                    fontWeight: 500,
                    color: "var(--mantine-color-waDark-6)",
                    userSelect: "none",
                    textAlign: "center",
                  }}
                >
                  {value}
                </Text>

                <ChevronRight onClick={increase} disabled={value >= max} />
              </Flex>
            </Flex>
          </Group>
        </Popover.Target>

        <Popover.Dropdown>
          <Group
            ref={ref}
            onKeyDown={getHotkeyHandler([["Enter", popoverOKButtonOnClick]])}
          >
            <TextInput
              flex={1}
              placeholder="Value"
              size="xs"
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
              }}
            />

            <Button h={30} m={0} onClick={popoverOKButtonOnClick}>
              Ok
            </Button>
          </Group>
        </Popover.Dropdown>
      </Popover>
    </Group>
  );
}
