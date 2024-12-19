import { Stack, Group, Text, useMantineTheme } from "@mantine/core";
import React from "react";
import { ParamItem } from "./ParamItem";

export function Prompt({
  cardName,
  inputsInfo,
  addonInputsInfo,
}: {
  cardName: string;
  inputsInfo: any;
  addonInputsInfo: any;
}) {
  return (
    <Stack p={20}>
      <Stack>
        <PromptTitle name={"Card Name"} value={cardName} />
        <PromptTitle name={""} value={"Basic Inputs"} />
        {Object.entries(inputsInfo).map(([key, value]) => {
          if (value) {
            return <ParamItem key={key} name={key} value={value} />;
          }
        })}
        <PromptTitle name={""} value={"Addon Inputs"} />
        {Object.entries(addonInputsInfo).map(([key, value]) => {
          if (value) {
            return <AddonInputInfo key={key} name={key} value={value} />;
          }
        })}
      </Stack>
    </Stack>
  );
}

function PromptTitle({ name, value }: { name: string; value: string }) {
  const theme = useMantineTheme();

  return (
    <Group bg={theme.colors.waLight[3]} p={10}>
      {name && (
        <Text c={theme.colors.waDark[8]} span size={"sm"}>
          {name}:
        </Text>
      )}
      <Text>{value}</Text>
    </Group>
  );
}

function AddonTitle({ name, value }: { name: string; value: string }) {
  const theme = useMantineTheme();

  return (
    <Group bg={theme.colors.waLight[3]} p={5} ml={40}>
      {name && (
        <Text c={theme.colors.waDark[8]} span>
          {name}:
        </Text>
      )}
      <Text
        style={{
          fontSize: "14px",
        }}
        pl={10}
      >
        {value}
      </Text>
    </Group>
  );
}

function AddonInputInfo({ name, value }: { name: string; value: any }) {
  if (Array.isArray(value)) {
    return (
      <Stack>
        <AddonTitle name={""} value={name} />
        {value.map((item) => {
          return Object.entries(item).map(([key, value]) => {
            if (value) {
              return <AddonItem key={key} name={key} value={value} />;
            }
          });
        })}
      </Stack>
    );
  }
  return <>/</>;
}

function AddonItem({ name, value }: { name: string; value: any }) {
  const theme = useMantineTheme();

  return (
    <Group ml={50}>
      <Text
        w={100}
        style={{
          textAlign: "right",
          fontSize: "14px",
        }}
      >
        {name}:
      </Text>
      <Text
        ml={20}
        p={5}
        px={15}
        maw={400}
        bg={theme.colors.waLight[5]}
        style={{
          maxLines: 5,
          maxWidth: "400px",
          wordBreak: "break-all",
        }}
      >
        {value}
      </Text>
    </Group>
  );
}
