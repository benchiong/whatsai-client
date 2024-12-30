import {
  CivitaiFileArrayType,
  CivitaiFileToDownLoadArrayType,
  CivitaiFileToDownloadType,
  CivitaiModelVersionType,
} from "../../data-type/civitai-data-type";
import {
  Modal,
  Stack,
  Group,
  Center,
  Title,
  Text,
  Button,
  useMantineTheme,
} from "@mantine/core";
import { BlurHashImage } from "../Image/BlurHashImage";
import { mapCivitaiModelTypeToWhatsAI } from "../../lib/utils";
import React, { useCallback, useEffect, useState } from "react";
import { ModelTypeSelector } from "./ModelTypeSelector";
import { downloadCivitaiModel } from "../../lib/api";
import { useModelDownloadingContext } from "../../providers/ModelDownloadingProvider";
import { civitSizeStr } from "../../data-type/helpers";

export function AddCivitAIModelModal({
  opened,
  civitModelVersion,
  onClose,
  onFileToDownloadChanged,
  onDownload,
}: {
  opened: boolean;
  civitModelVersion: CivitaiModelVersionType;
  onClose: () => void;
  onFileToDownloadChanged: (
    allFilesToDownload: CivitaiFileToDownLoadArrayType,
  ) => void;
  onDownload: () => void;
}) {
  const theme = useMantineTheme();

  const modelDownloadingContext = useModelDownloadingContext();
  const [filesToDownload, setFilesToDownload] =
    useState<CivitaiFileToDownLoadArrayType>([]);
  const [downloading, setDownloading] = useState(false);

  // stupid way to solve civitai same filename problem. todo: make it better.
  // case: https://civitai.com/models/618692/flux
  const filterSameFilenameFiles = useCallback((files: CivitaiFileArrayType) => {
    let filteredFiles = [];
    let filenames = [];
    for (const file of files) {
      const fileName = file["name"];
      if (filenames.indexOf(fileName) == -1) {
        filenames.push(fileName);
        filteredFiles.push(file);
      }
    }
    return filteredFiles;
  }, []);

  useEffect(() => {
    const files = filterSameFilenameFiles(civitModelVersion.files);
    const filesToDownLoad: CivitaiFileToDownLoadArrayType = files.map(
      (file) => {
        return {
          civitaiFile: file,
          modelType: mapCivitaiModelTypeToWhatsAI(file.type),
        };
      },
    );
    onFileToDownloadChanged(filesToDownLoad);
    setFilesToDownload(filesToDownLoad);
  }, [civitModelVersion]);

  return (
    <Modal
      opened={opened}
      withCloseButton={true}
      title={"Download CivitAI model"}
      onClose={() => {
        setFilesToDownload([]);
        onClose();
      }}
      radius={10}
      transitionProps={{ duration: 100 }}
      size={"lg"}
    >
      <Group justify={"center"}>
        <Stack align={"start"} w={500}>
          {civitModelVersion.model?.name && (
            <Title order={4}>
              <Text c={theme.colors.waDark[8]} span size={"sm"}>
                Model Name:{" "}
              </Text>
              {`${civitModelVersion.model.name}`}
            </Title>
          )}
          <Title order={4}>
            <Text c={theme.colors.waDark[8]} span size={"sm"}>
              {"Model Version:"}{" "}
            </Text>
            {`${civitModelVersion.name}`}
          </Title>
          <Center w={500} h={300} my={20}>
            {civitModelVersion.images[0].url &&
              civitModelVersion.images[0].hash && (
                <BlurHashImage
                  width={200}
                  height={300}
                  src={civitModelVersion.images[0].url!}
                  alt={"image"}
                  hash={civitModelVersion.images[0].hash!}
                />
              )}
          </Center>
          <Title order={5}>
            <Text c={theme.colors.waDark[8]} span size={"sm"}>
              Base Model:{" "}
            </Text>
            {civitModelVersion.baseModel}
          </Title>
          <Title order={5}>
            <Text c={theme.colors.waDark[8]} span size={"sm"}>
              Model Type:{" "}
            </Text>
            {civitModelVersion.baseModelType ?? civitModelVersion.model?.type}
          </Title>
          <Stack align={"center"} mt={10}>
            {filesToDownload.map(
              (fileToDownload: CivitaiFileToDownloadType, index) => {
                let file = fileToDownload.civitaiFile;
                if (file.downloadUrl) {
                  return (
                    <Group w={500} key={file.id}>
                      <Group
                        bg={theme.colors.waLight[3]}
                        p={10}
                        style={{
                          borderRadius: "3px",
                        }}
                        align={"start"}
                      >
                        <Text
                          w={220}
                          style={{
                            fontSize: "12px",
                            textAlign: "start",
                            overflow: "hidden",
                            "text-overflow": "ellipsis",
                          }}
                          lineClamp={1}
                          truncate={"start"}
                        >
                          {file.name}
                        </Text>
                        <Text
                          w={60}
                          style={{
                            fontSize: "12px",
                            textAlign: "start",
                          }}
                        >
                          {civitSizeStr(file.sizeKB)}
                        </Text>
                      </Group>

                      {filesToDownload[index] && (
                        <ModelTypeSelector
                          width={140}
                          onChange={(value) => {
                            const fileToDownload = {
                              ...filesToDownload[index],
                            };
                            fileToDownload.modelType = value;
                            filesToDownload[index] = fileToDownload;
                            onFileToDownloadChanged(filesToDownload);
                          }}
                          key={filesToDownload[index].civitaiFile.id}
                          modelType={filesToDownload[index].modelType}
                        />
                      )}
                    </Group>
                  );
                }
              },
            )}
          </Stack>
          <Center w={500} my={40}>
            <Button
              h={40}
              w={160}
              onClick={() => {
                setDownloading(true);

                if (civitModelVersion.images[0].url) {
                  downloadCivitaiModel(
                    filesToDownload,
                    civitModelVersion,
                    civitModelVersion.images[0].url!,
                  )
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
      </Group>
    </Modal>
  );
}
