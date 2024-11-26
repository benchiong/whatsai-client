import {
  AspectRatio,
  Group,
  Stack,
  Text,
  RingProgress,
  Overlay,
  Center,
  useMantineTheme,
} from "@mantine/core";
import { useModelDownloadingContext } from "../../providers/ModelDownloadingProvider";
import React, { useCallback } from "react";
import { ModelDownloadingInfoType } from "../../data-type/model";
import { ImageLocal } from "../Image/ImageLocal";

import { civitSizeStr } from "../../data-type/helpers";

export function ModelDownloading() {
  const theme = useMantineTheme();
  const modelDownloadingContext = useModelDownloadingContext();

  const downloadingInfos = modelDownloadingContext.downloadingModels;

  if (downloadingInfos && downloadingInfos.length > 0) {
    return (
      <Stack m={20} bg={theme.colors.waLight[4]}>
        <Group justify={"space-start"} h={36} bg={theme.colors.waLight[3]}>
          <Text
            c={theme.colors.waDark[3]}
            ml={20}
            style={{
              textAlign: "start",
              fontSize: "14px",
              fontWeight: 300,
              height: "30px",
              lineHeight: "30px",
              position: "sticky",
              top: "0px",
              zIndex: 100,
            }}
          >
            Downloading Models
          </Text>

          <Text
            span
            mr={10}
            px={8}
            py={2}
            style={{
              background: "var(--mantine-color-waLight-2)",
              borderRadius: "10px",
              fontSize: "12px",
              fontWeight: 300,
            }}
          >{`${downloadingInfos.length ?? 0}`}</Text>
        </Group>

        <Group p={20}>
          {downloadingInfos.map((info) => {
            return <ModelDownloadingItem info={info} key={info.url} />;
          })}
        </Group>
      </Stack>
    );
  } else {
    return <></>;
  }
}

function ModelDownloadingItem({ info }: { info: ModelDownloadingInfoType }) {
  const theme = useMantineTheme();

  const progressStr =
    info.progress > 0 ? `${(info.progress * 100).toFixed(1)}%` : "-";

  const readableEta = useCallback((eta: number) => {
    if (eta > 60) {
      const minutes = (eta / 60).toFixed(0);
      const seconds = (eta % 60).toFixed(0);
      return `${minutes}m${seconds}s`;
    } else {
      return `${eta.toFixed(0)}s`;
    }
  }, []);

  return (
    <Group>
      <Stack
        pt={10}
        w={200}
        h={300}
        bg={theme.colors.waLight[1]}
        align={"center"}
      >
        <AspectRatio
          mt={10}
          ratio={140 / 210}
          maw={400}
          style={{
            position: "relative",
          }}
        >
          <ImageLocal
            localPath={info.model_info.image_path}
            width={140}
            height={210}
            objectFit={"cover"}
          />

          <Overlay
            radius={"md"}
            color={theme.colors.waLight[2]}
            backgroundOpacity={0.7}
            fixed={false}
          >
            <Stack w={140} h={210} align={"center"} justify={"center"}>
              {info.eta && (
                <Text
                  c={theme.colors.waDark[7]}
                  fw={700}
                  ta="center"
                  h={40}
                  style={{
                    fontSize: "12px",
                  }}
                >
                  {`ETA: ${readableEta(info.eta!)}`}
                </Text>
              )}
              <Center flex={1}>
                <RingProgress
                  size={100}
                  thickness={6}
                  rootColor={theme.colors.waLight[6]}
                  label={
                    <Text
                      c={theme.colors.waDark[7]}
                      fw={700}
                      ta="center"
                      size="sm"
                    >
                      {progressStr}
                    </Text>
                  }
                  sections={[
                    {
                      value: info.progress * 100,
                      color: theme.colors.phOrange[0],
                    },
                  ]}
                />
              </Center>

              <Text
                c={theme.colors.waDark[7]}
                fw={700}
                ta="center"
                h={40}
                style={{
                  fontSize: "12px",
                }}
              >
                {`${civitSizeStr(info.downloaded_size, 1)} / ${civitSizeStr(info.total_size, 1)}`}
              </Text>
            </Stack>
          </Overlay>
        </AspectRatio>
        <Text
          lineClamp={2}
          w={100}
          mb={10}
          style={{
            fontSize: "10px",
            fontWeight: "500",
            wordBreak: "break-all",
          }}
        >{`${info.model_info.file_name}`}</Text>
      </Stack>
    </Group>
  );
}
