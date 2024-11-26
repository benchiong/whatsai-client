import {
  Center,
  Group,
  Popover,
  ScrollArea,
  Stack,
  Text,
  useMantineTheme,
} from "@mantine/core";
import React, { useEffect, useState } from "react";
import { getRecentlyUsed } from "../../lib/api";
import { Refresh } from "./Refresh";
import { Close } from "./Close";
import { ImageLocal } from "../Image/ImageLocal";
import { MediaArrayType, MediaType } from "../../data-type/media";

export function RecentlyUsedCard({
  children,
  mediaType,
  subKey = "",
  opened,
  width = 500,
  onMediaSelected,
  close,
}: {
  children: React.ReactNode;
  mediaType: string;
  subKey?: string;
  opened: boolean;
  width?: number;
  onMediaSelected: (media: MediaType) => void;
  close: () => void;
}) {
  const theme = useMantineTheme();
  const [medias, setMedias] = useState<MediaArrayType>([]);
  const load = () => {
    getRecentlyUsed(mediaType, subKey)
      .then((r) => setMedias(r))
      .catch((e) => {
        console.log(e);
      });
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <Popover
      shadow="md"
      radius={"sm"}
      position={"right"}
      opened={opened && medias.length > 0}
      zIndex={490}
    >
      <Popover.Target>{children}</Popover.Target>
      <Popover.Dropdown p={0}>
        <Stack gap={0}>
          <Group
            h={44}
            w={"100%"}
            px={20}
            bg={theme.colors.waLight[2]}
            justify={"space-between"}
          >
            <Group w={"100%"} justify={"space-between"}>
              <Group gap={10}>
                <Text
                  h={20}
                  style={{
                    lineHeight: "20px",
                    fontSize: "14px",
                    fontWeight: 300,
                  }}
                >
                  {"Select from recently used"}
                </Text>
                <Refresh
                  width={20}
                  height={20}
                  onClick={() => {
                    load();
                  }}
                  text={"Refresh images"}
                />
              </Group>
              <Close onClick={() => close()} />
            </Group>

            {/*<Close onClick={() => set()} />*/}
          </Group>

          <ScrollArea h={400} w={width}>
            <Group mx={20} pt={20} pb={50}>
              {medias &&
                medias.map((media) => {
                  return (
                    <RecentlyUsedItem
                      key={media.file_path}
                      media={media}
                      onClick={(media) => {
                        onMediaSelected(media);
                      }}
                    />
                  );
                })}
            </Group>
          </ScrollArea>
        </Stack>
      </Popover.Dropdown>
    </Popover>
  );
}

function RecentlyUsedItem({
  media,
  onClick,
}: {
  media: MediaType;
  onClick: (media: MediaType) => void;
}) {
  const theme = useMantineTheme();
  return (
    <Center
      bg={theme.colors.waLight[3]}
      style={{
        cursor: "pointer",
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick(media);
      }}
    >
      <ImageLocal
        localPath={media.file_path ?? ""}
        width={70}
        height={105}
        objectFit={"contain"}
      />
    </Center>
  );
}
