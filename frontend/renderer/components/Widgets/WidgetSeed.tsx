import {
  Button,
  Flex,
  Group,
  Popover,
  Text,
  TextInput,
  useMantineTheme,
} from "@mantine/core";
import { getHotkeyHandler, useClickOutside } from "@mantine/hooks";
import { useCallback, useEffect, useState } from "react";
import { LabelName } from "./LabelName";
import { IconDice3 } from "@tabler/icons-react";
import { useCardContext } from "../../providers/CardProvider";

export function WidgetSeed({
  onChange,
  defaultValue = null,
  text = "Seed",
  max = 0xffffffffffffff,
  min = 0,
  width = "100%",
  height = 38,
}: {
  text?: string;
  defaultValue?: number | null;
  max?: number;
  min?: number;
  width?: number | string;
  height?: number;
  onChange?: (value: number) => void;
}) {
  const theme = useMantineTheme();
  const cardContext = useCardContext();

  // todo: no grace here, find a better way.
  const generationSeed = useCallback(() => {
    const innerSeedGenerate = () => {
      const length = max.toString().length;
      const randomLength = Math.max(8, Math.ceil(Math.random() * (length + 1)));
      let result = 0;
      for (let i = 1; i <= randomLength; i++) {
        result += Math.floor(Math.pow(10, i) * Math.random());
      }
      return result;
    };

    let seed = innerSeedGenerate();
    while (seed < min || seed > max) {
      seed = innerSeedGenerate();
    }

    return seed;
  }, []);

  const [value, setValue] = useState<number>(defaultValue ?? generationSeed());

  const [inputValue, setInputValue] = useState<number>(value);
  const [opened, setOpened] = useState<boolean>(false);
  const ref = useClickOutside(() => setOpened(false));

  useEffect(() => {
    setValue(defaultValue ?? generationSeed());
  }, [defaultValue]);

  useEffect(() => {
    cardContext.registerOnGenerateCallback(() => {
      // todo: 1.there is a bug here, when the callback run, addons will be clear, find why and fix.
      // todo: 2.consider if the callback way is a good way, is there a better way to solve this.
      // const randomValue = generationSeed();
      // setValue(randomValue);
      // innerOnChange(randomValue);
    }, "Seed");
  }, []);

  const innerOnChange = (value: number) => {
    onChange && onChange(value);
  };

  const popoverOKButtonOnClick = () => {
    setOpened(false);
    if (isNaN(inputValue)) {
      setValue(defaultValue ?? generationSeed());
      innerOnChange(defaultValue ?? generationSeed());
    } else {
      const value = Math.min(max, Math.max(min, inputValue));
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

              <Text
                style={{
                  marginLeft: "30px",
                  fontSize: "14px",
                  fontWeight: 500,
                  color: "var(--mantine-color-waDark-6)",
                  userSelect: "none",
                  textAlign: "center",
                }}
              >
                {value}
              </Text>

              <IconDice3
                style={{
                  color: "var(--mantine-color-primary-3)",
                  cursor: "pointer",
                  height: "22px",
                  width: "22px",
                  strokeWidth: "1px",
                }}
                onClick={(event) => {
                  event.stopPropagation();
                  const randomValue = generationSeed();
                  setValue(randomValue);
                  innerOnChange(randomValue);
                }}
              />
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
                setInputValue(parseInt(e.target.value));
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
