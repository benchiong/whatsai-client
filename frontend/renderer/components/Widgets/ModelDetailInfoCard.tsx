import React from "react";
import { ModelInfoType } from "../../data-type/model";
import {
  Group,
  Popover,
  Center,
  Image,
  Stack,
  Text,
  useMantineTheme,
} from "@mantine/core";
import Link from "next/link";
import { civitaiUrl, civitSizeStr } from "../../data-type/helpers";
import { IconX } from "@tabler/icons-react";

export function ModelDetailInfoCard({
  children,
  model,
  close,
  opened = false,
}: {
  children: React.ReactNode;
  model: ModelInfoType;
  opened: boolean;
  close: () => void;
}) {
  const theme = useMantineTheme();
  return (
    <Popover
      width={420}
      shadow="md"
      radius={"sm"}
      position={"right"}
      withArrow
      opened={opened}
      zIndex={490}
    >
      <Popover.Target>{children}</Popover.Target>
      <Popover.Dropdown>
        <Stack
          style={{
            position: "relative",
          }}
          mih={200}
          justify={"center"}
        >
          <Stack
            gap={5}
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
            }}
          >
            {model.civit_model?.model?.name && (
              <Text
                c={theme.colors.waLight[8]}
                style={{
                  fontSize: "12px",
                  fontWeight: "500",
                  wordBreak: "break-all",
                }}
              >
                {`Model Name:   ${model.civit_model?.model?.name}`}
              </Text>
            )}

            {model.civit_model?.name && (
              <Text
                c={theme.colors.waLight[8]}
                style={{
                  fontSize: "12px",
                  fontWeight: "500",
                  wordBreak: "break-all",
                }}
              >
                {`Version Name:   ${model.civit_model?.name}`}
              </Text>
            )}

            {model.civit_model?.baseModel && (
              <Text
                c={theme.colors.waLight[8]}
                style={{
                  fontSize: "12px",
                  fontWeight: "500",
                }}
              >{`Base Model:   ${model.civit_model?.baseModel}`}</Text>
            )}

            {model.file_name && (
              <Text
                c={theme.colors.waLight[8]}
                style={{
                  fontSize: "12px",
                  fontWeight: "500",
                  wordBreak: "break-all",
                }}
              >
                {`File Name:   ${model.file_name}`}
              </Text>
            )}

            {model.size_kb && (
              <Text
                c={theme.colors.waLight[8]}
                style={{
                  fontSize: "12px",
                  fontWeight: "500",
                  wordBreak: "break-all",
                }}
              >
                {`File Size:   ${civitSizeStr(model.size_kb, 1)}`}
              </Text>
            )}

            <Text
              c={theme.colors.waLight[8]}
              style={{
                fontSize: "12px",
                fontWeight: "500",
                wordBreak: "break-all",
              }}
            >
              {`Local Path:   ${model.local_path}`}
            </Text>
          </Stack>
          {civitaiUrl(model) && (
            <Link
              href={civitaiUrl(model)!}
              target={"_blank"}
              onClick={(e) => e.stopPropagation()}
            >
              <Group gap={5} my={5}>
                <Image h={16} src={"/images/civitai-icon.png"} w={16} />

                <Text
                  span
                  c={theme.colors.waDark[8]}
                  style={{
                    fontSize: "12px",
                    fontWeight: "500",
                  }}
                >
                  Civitai URL
                </Text>
              </Group>
            </Link>
          )}

          <Center
            style={{
              position: "absolute",
              top: "0px",
              right: "0px",
            }}
          >
            <IconX
              style={{
                color: "var(--mantine-color-waLight-9)",
                cursor: "pointer",
                height: `20px`,
                width: `20px`,
                strokeWidth: "1px",
              }}
              onClick={(e) => {
                e.stopPropagation();
                close();
              }}
            />
          </Center>
        </Stack>
      </Popover.Dropdown>
    </Popover>
  );
}
