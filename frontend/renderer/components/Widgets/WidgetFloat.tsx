import {
  Group,
  Flex,
  Text,
  TextInput,
  Button,
  Popover,
  useMantineTheme,
} from "@mantine/core";
import { useCallback, useState } from "react";
import { getHotkeyHandler, useClickOutside } from "@mantine/hooks";
import { ChevronRight } from "./ChevronRight";
import { ChevronLeft } from "./ChevronLeft";
import { LabelName } from "./LabelName";
import { showNormalNotification } from "../../utils/notifications";

export function WidgetFloat({
  text,
  defaultValue,
  onChange,
  step = 1.0,
  max = 100.0,
  min = 0.0,
  round = 2,
  width = "100%",
  height = 38,
}: {
  text: string;
  defaultValue: number;
  step?: number;
  max?: number;
  min?: number;
  round?: number;
  width?: number | string;
  height?: number;
  onChange?: (value: number) => void;
}) {
  const innerOnChange = (value: string) => {
    onChange && onChange(parseFloat(value));
  };
  const theme = useMantineTheme();

  const [value, setValue] = useState(defaultValue.toFixed(round));

  const [inputValue, setInputValue] = useState(value);
  const [opened, setOpened] = useState(false);
  const ref = useClickOutside(() => setOpened(false));

  const increase = () => {
    setValue((prevValue) => {
      const newValue = parseFloat(prevValue) + step;
      const value = Math.min(newValue, max).toFixed(round);
      if (value == max.toFixed(round)) {
        showNormalNotification({
          title: "Reach the maximum value",
          message: `Value of ${text}: ${value} has reached the maximum.`,
        });
      }
      innerOnChange(value);
      return value;
    });
  };

  const decrease = () => {
    setValue((prevValue) => {
      const newValue = parseFloat(prevValue) - step;
      const value = Math.max(newValue, min).toFixed(round);
      if (value == min.toFixed(round)) {
        showNormalNotification({
          title: "Reach the minimum value",
          message: `Value of ${text}: ${value} has reached the minimum.`,
        });
      }
      innerOnChange(value);
      return value;
    });
  };

  const popoverOKButtonOnClick = () => {
    setOpened(false);
    const inputFloatValue = parseFloat(inputValue);
    if (isNaN(inputFloatValue)) {
      setValue("" + defaultValue);
      innerOnChange(value);
    } else {
      const value = Math.min(max, Math.max(min, inputFloatValue)).toFixed(
        round,
      );
      setValue(value);
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

              <Flex
                justify={"space-between"}
                align={"center"}
                w={"100%"}
                ml={10}
                flex={1}
              >
                <ChevronLeft
                  onClick={decrease}
                  disabled={parseFloat(value) <= min}
                />

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

                <ChevronRight
                  onClick={increase}
                  disabled={parseFloat(value) >= max}
                />
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
