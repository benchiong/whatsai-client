import {
  Button,
  Center,
  FileInput,
  Group,
  Stack,
  useMantineTheme,
} from "@mantine/core";
import React, { useRef, useState } from "react";
import { Close } from "./Close";
import { LabelSingleLine } from "./LabelSingleLine";
import { ImageLocal } from "../Image/ImageLocal";
import { RecentlyUsedCard } from "./RecentlyUsedCard";
import { addRecentlyUsed } from "../../lib/api";
import { IconClock } from "@tabler/icons-react";

export function WidgetImage({
  onChange,
  text = "Select Image",
  title = "Select Image",
  width = "100%",
  defaultImage = null,
  ruSubKey = "", // ru: recently used
}: {
  title?: string;
  text?: string;
  onChange: (imagePath: string | null) => void;
  width?: number | string;
  height?: number | string;
  defaultImage?: string | null;
  ruSubKey?: string;
}) {
  const theme = useMantineTheme();
  const imageWidth = 150;
  const imageHeight = 210;
  const ref = useRef<HTMLButtonElement | null>(null);

  const [image, setImage] = useState<string | null>(defaultImage);
  const [recentlyUsedOpened, setRecentlyUsedOpened] = useState(false);

  const AddToRecent = (image_path: string) => {
    addRecentlyUsed("image", ruSubKey, image_path)
      .then((r) => {
        // console.log("add to ru:", r);
      })
      .catch((e) => {
        console.log(e);
      });
  };

  return (
    <Stack
      w={width}
      bg={theme.colors.waLight[3]}
      style={{
        borderRadius: "10px",
      }}
    >
      <Group justify={"space-between"} align={"center"}>
        <LabelSingleLine text={text} />
        <Center mr={10} mt={10}>
          <IconClock
            style={{
              color: "var(--mantine-color-primary-3)",
              cursor: "pointer",
              height: "22px",
              width: "22px",
              strokeWidth: "1px",
            }}
            onClick={(e) => setRecentlyUsedOpened(true)}
          />
        </Center>
      </Group>
      <Stack align={"center"}>
        <RecentlyUsedCard
          // key={image}
          mediaType={"image"}
          opened={recentlyUsedOpened}
          subKey={ruSubKey}
          onMediaSelected={(media) => {
            setImage(media.file_path);
            onChange(media.file_path);
            AddToRecent(media.file_path);
          }}
          close={() => setRecentlyUsedOpened(false)}
        >
          <Center
            h={imageHeight}
            w={imageWidth}
            bg={theme.colors.waLight[2]}
            style={{
              borderRadius: "5px",
              position: "relative",
              cursor: "pointer",
            }}
          >
            {image && (
              <ImageLocal
                localPath={image}
                width={imageWidth}
                height={imageHeight}
                key={text}
                objectFit={"contain"}
              />
            )}
            {image && (
              <Center
                style={{
                  position: "absolute",
                  right: "-6px",
                  top: "-6px",
                  background: "var(--mantine-color-waDark-1)",
                  borderRadius: "10px",
                  opacity: 0.3,
                }}
              >
                <Close
                  width={14}
                  height={14}
                  onClick={() => {
                    setImage(null);
                    onChange(null);
                  }}
                />
              </Center>
            )}

            <Center
              hidden={true}
              style={{
                position: "absolute",
                fontSize: "10px",
                bottom: "0px",
                left: "0px",
                width: "100%",
                height: "50px",
              }}
            >
              <Button
                hidden={true}
                w={100}
                h={25}
                opacity={0.6}
                onClick={(e) => ref.current?.click()}
                style={{
                  fontSize: "10px",
                }}
              >
                {title}
              </Button>
            </Center>
          </Center>
        </RecentlyUsedCard>

        <Center
          hidden={true}
          h={0}
          w={0}
          style={{
            overflow: "hidden",
          }}
        >
          <FileInput
            ref={ref}
            accept={"image/*"}
            onChange={(file) => {
              setImage(file?.path ?? null);
              onChange(file?.path ?? null);
              if (file?.path) {
                AddToRecent(file.path);
              }
            }}
          />
        </Center>
      </Stack>
    </Stack>
  );
}
