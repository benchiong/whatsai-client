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
import { getRecentlyUsed, removeRecentlyUsed } from "../../lib/api";
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
  subKey?: string; // use to locate to inpainting /controlnet ...
  opened: boolean;
  width?: number;
  onMediaSelected: (media: MediaType) => void;
  close: () => void;
}) {
  const theme = useMantineTheme();
  const [medias, setMedias] = useState<MediaArrayType>([]);

  useEffect(() => {
    getRecentlyUsed(mediaType, subKey)
      .then((r) => setMedias(r))
      .catch((e) => {
        console.log(e);
      });
  }, [opened]);

  return (
    <Popover
      shadow="md"
      radius={"sm"}
      position={"right"}
      opened={opened}
      zIndex={690}
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
                  asyncOperation={async () => {
                    const medias = await getRecentlyUsed(mediaType, subKey);
                    if (medias.length > 0) {
                      setMedias(medias);
                    }
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
                      asyncOnRemove={async () => {
                        const mediasAfterRemove = await removeRecentlyUsed(
                          mediaType,
                          subKey,
                          media.file_path,
                        );
                        if (mediasAfterRemove) {
                          setMedias(mediasAfterRemove);
                        }
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
  asyncOnRemove,
}: {
  media: MediaType;
  onClick: (media: MediaType) => void;
  asyncOnRemove: () => Promise<void>;
}) {
  const theme = useMantineTheme();
  const [closeVisible, setCloseVisible] = useState(false);
  return (
    <Center
      onMouseEnter={() => setCloseVisible(true)}
      onMouseLeave={() => setCloseVisible(false)}
      bg={theme.colors.waLight[3]}
      style={{
        cursor: "pointer",
        position: "relative",
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
      {closeVisible && (
        <Center
          w={20}
          h={20}
          bg={theme.colors.waLight[6]}
          style={{
            position: "absolute",
            top: "-10px",
            right: "-10px",
            borderRadius: 10,
          }}
        >
          <Close
            width={18}
            height={18}
            onClick={() => {
              asyncOnRemove()
                .then((r) => {})
                .catch((e) => {});
            }}
          />
        </Center>
      )}
    </Center>
  );
}
