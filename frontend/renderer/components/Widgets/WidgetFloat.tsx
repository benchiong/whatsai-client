import {
  Group,
  Flex,
  Text,
  TextInput,
  Button,
  Popover,
  useMantineTheme,
} from "@mantine/core";
import { useCallback, useEffect, useState } from "react";
import { getHotkeyHandler, useClickOutside } from "@mantine/hooks";
import { ChevronRight } from "./ChevronRight";
import { ChevronLeft } from "./ChevronLeft";
import { LabelName } from "./LabelName";
import { showNormalNotification } from "../../utils/notifications";

export function WidgetFloat({
  text,
  value,
  onChange,
  step = 1.0,
  max = 100.0,
  min = 0.0,
  round = 2,
  width = "100%",
  height = 38,
}: {
  text: string;
  value: number;
  step?: number;
  max?: number;
  min?: number;
  round?: number;
  width?: number | string;
  height?: number;
  onChange?: (value: number) => void;
}) {
  const innerOnChange = (value: number) => {
    onChange && onChange(roundToPrecision(value, round));
  };
  const theme = useMantineTheme();

  const [inputValue, setInputValue] = useState(value.toFixed(round));

  const [opened, setOpened] = useState(false);
  const ref = useClickOutside(() => setOpened(false));

  useEffect(() => {
    setInputValue(value.toFixed(round));
  }, [value]);

  const increase = useCallback(() => {
    let newValue = value + step;
    newValue = Math.min(newValue, max);
    if (newValue >= max) {
      showNormalNotification({
        title: "Reach the maximum value",
        message: `Value of ${text}: ${newValue} has reached the maximum.`,
      });
    }
    innerOnChange(newValue);
  }, [value]);

  const decrease = useCallback(() => {
    let newValue = value - step;
    newValue = Math.max(newValue, min);
    if (newValue <= min) {
      showNormalNotification({
        title: "Reach the minimum value",
        message: `Value of ${text}: ${newValue} has reached the minimum.`,
      });
    }
    innerOnChange(newValue);
  }, [value]);

  const popoverOKButtonOnClick = () => {
    setOpened(false);
    const inputFloatValue = parseFloat(inputValue);
    if (isNaN(inputFloatValue)) {
      innerOnChange(value);
    } else {
      const value = Math.min(max, Math.max(min, inputFloatValue));
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
                  {value.toFixed(round)}
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

function roundToPrecision(value: number, round: number): number {
  const factor = Math.pow(10, round);
  return Math.round(value * factor) / factor;
}
