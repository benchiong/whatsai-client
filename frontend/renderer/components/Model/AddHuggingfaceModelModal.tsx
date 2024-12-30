import {
  Button,
  Center,
  Group,
  Modal,
  Stack,
  Text,
  useMantineTheme,
} from "@mantine/core";
import { ModelTypeSelector } from "./ModelTypeSelector";
import React, { useState } from "react";
import { civitSizeStr } from "../../data-type/helpers";
import { downloadCivitaiModel, downloadHuggingfaceModel } from "../../lib/api";
import { useModelDownloadingContext } from "../../providers/ModelDownloadingProvider";

export function AddHuggingfaceModelModal({
  opened,
  modelSize,
  onClose,
  onDownload,
  downloadUrl,
}: {
  opened: boolean;
  modelSize: number;
  onClose: () => void;
  onDownload: () => void;
  downloadUrl: string;
}) {
  const [modelType, setModelType] = useState<string | null>(null);
  const theme = useMantineTheme();
  const [downloading, setDownloading] = useState(false);
  const modelDownloadingContext = useModelDownloadingContext();

  return (
    <Modal
      opened={opened}
      withCloseButton={true}
      title={"Download Huggingface model"}
      onClose={() => {
        onClose();
      }}
      radius={10}
      transitionProps={{ duration: 100 }}
      size={"lg"}
    >
      <Stack>
        <Group
          p={10}
          style={{
            borderRadius: "3px",
          }}
          align={"center"}
        >
          <Text
            style={{
              fontSize: "14px",
              textAlign: "start",
              overflow: "hidden",
              "text-overflow": "ellipsis",
            }}
            lineClamp={1}
          >
            {"File to Download:"}
          </Text>
          <Text
            bg={theme.colors.waLight[3]}
            p={5}
            style={{
              fontSize: "12px",
              textAlign: "start",
              overflow: "hidden",
              "text-overflow": "ellipsis",
            }}
            lineClamp={1}
          >
            {downloadUrl}
          </Text>
        </Group>

        <Group
          p={10}
          style={{
            borderRadius: "3px",
          }}
          align={"center"}
        >
          <Text
            style={{
              fontSize: "14px",
              textAlign: "start",
              overflow: "hidden",
              "text-overflow": "ellipsis",
              lineHeight: "20px",
            }}
            lineClamp={1}
          >
            {"File Size:"}
          </Text>
          <Text
            bg={theme.colors.waLight[3]}
            p={5}
            style={{
              fontSize: "12px",
              lineHeight: "20px",
            }}
            lineClamp={1}
          >
            {civitSizeStr(modelSize, 2)}
          </Text>
        </Group>

        <Group
          p={10}
          style={{
            borderRadius: "3px",
          }}
          align={"center"}
        >
          <Text
            style={{
              fontSize: "14px",
              textAlign: "start",
              overflow: "hidden",
              "text-overflow": "ellipsis",
              lineHeight: "20px",
            }}
            lineClamp={1}
          >
            {"Select Model Type:"}
          </Text>
          <ModelTypeSelector
            width={140}
            onChange={(value) => {
              setModelType(value);
            }}
            modelType={modelType}
          />
        </Group>

        <Center w={500} my={40}>
          <Button
            h={40}
            w={160}
            disabled={!modelType}
            onClick={() => {
              if (modelType) {
                setDownloading(true);
                downloadHuggingfaceModel(downloadUrl, modelType)
                  .then((r) => {
                    setDownloading(false);
                    modelDownloadingContext.startLoop();
                    onDownload();
                  })
                  .catch((e) => {
                    setDownloading(false);
                    console.error(e);
                  });
              }
            }}
            loading={downloading}
          >
            Download
          </Button>
        </Center>
      </Stack>
    </Modal>
  );
}
