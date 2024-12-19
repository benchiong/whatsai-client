import React, { useCallback, useEffect, useState } from "react";
import Head from "next/head";
import {
  Group,
  TextInput,
  Stack,
  Button,
  useMantineTheme,
  Center,
  Tooltip,
  Text,
} from "@mantine/core";
import { ModelInfoArrayType, ModelsRecordType } from "../data-type/model";
import { ModelsRecord } from "../components/Model/ModelsRecord";
import { getCivitaiModelVersionInfo, getModels } from "../lib/api";
import { getKeyOfModelsRecord } from "../lib/utils";
import { ModelDirModal } from "../components/Model/ModelDirModal";
import { IconFolder } from "@tabler/icons-react";
import { OtherUIDirModal } from "../components/Model/OtherUIDirModal";
import { showErrorNotification } from "../utils/notifications";
import {
  CivitaiFileToDownLoadArrayType,
  CivitaiModelVersionType,
} from "../data-type/civitai-data-type";
import { AddCivitAIModelModal } from "../components/Model/AddCivitAIModelModal";
import { ModelDownloadingContextProvider } from "../providers/ModelDownloadingProvider";
import { ModelDownloading } from "../components/Model/ModelDownloading";

export default function ModelPage() {
  const theme = useMantineTheme();
  const [models, setModels] = useState<ModelInfoArrayType>([]);
  const [url, setUrl] = useState("");
  const [requesting, setRequesting] = useState(false); // requesting civitAI

  const [civitVersionInfo, setCivitVersionInfo] =
    useState<CivitaiModelVersionType | null>(null);
  const [filesToDownload, setFilesToDownload] =
    useState<CivitaiFileToDownLoadArrayType>([]);
  const [addModelOpened, setAddModelOpened] = useState(false);

  const [currentModelTypeName, setCurrentModelTypeName] = useState("");
  const [dirModalOpened, setDirModalOpened] = useState(false);
  const [otherUIDirModalOpened, setOtherUIDirModelOpened] = useState(false);

  const getAllModels = useCallback(() => {
    getModels()
      .then((models) => {
        setModels(models);
      })
      .catch((e) => console.log("getAllModels error:", e));
  }, []);

  useEffect(() => {
    getAllModels();
  }, []);

  return (
    <ModelDownloadingContextProvider>
      <Head>
        <title>Models</title>
      </Head>
      <Stack>
        <Group
          p={15}
          px={20}
          bg={theme.colors.waLight[0]}
          w={"100%"}
          style={{
            borderRadius: "5px",
            position: "sticky",
            top: "0px",
            zIndex: 210,
          }}
        >
          <Tooltip
            label={"Add WebUI/ComfyUI local models."}
            zIndex={500}
            radius={5}
            bg={theme.colors.waLight[6]}
            color={theme.colors.waLight[9]}
            style={{
              fontSize: "12px",
            }}
          >
            <Center
              ml={15}
              style={{
                cursor: "pointer",
              }}
              onClick={(e) => {
                e.stopPropagation();
                setOtherUIDirModelOpened(true);
              }}
            >
              <IconFolder
                style={{
                  cursor: "pointer",
                  height: "20px",
                  width: "20px",
                  strokeWidth: "2px",
                  stroke: "var(--mantine-color-primary-3)",
                }}
              />

              <Text
                ml={6}
                style={{
                  fontSize: "12px",
                  fontWeight: 400,
                  color: "var(--mantine-color-primary-3)",
                }}
              >
                WebUI/ComfyUI
              </Text>
            </Center>
          </Tooltip>

          <TextInput
            placeholder={`URL of Civitai model(Checkpoint/LoRA/Ti/Hyper) to add. (e.g. https://civitai.com/models/XXX...)`}
            flex={1}
            radius={"sm"}
            onChange={(e) => setUrl(e.target.value)}
          />
          <Button
            mr={5}
            loading={requesting}
            disabled={!url}
            onClick={() => {
              setRequesting(true);
              getCivitaiModelVersionInfo(url)
                .then((r) => {
                  setRequesting(false);
                  if (r.error) {
                    showErrorNotification({
                      error: Error("Request civitAI failed."),
                      reason: r.error.toString(),
                    });
                  } else {
                    setCivitVersionInfo(r.model_version_info);
                    setAddModelOpened(true);
                  }
                })
                .catch((e) => {
                  setRequesting(false);
                  showErrorNotification({
                    error: Error(e),
                    reason: e.reason,
                  });
                });
            }}
          >{`Add CivitAI model`}</Button>
        </Group>
        <ModelDownloading />
        {models.map((modelsRecord: ModelsRecordType) => {
          return (
            <ModelsRecord
              modelsRecord={modelsRecord}
              key={getKeyOfModelsRecord(modelsRecord)}
              openDirModel={(opened, typeName) => {
                setCurrentModelTypeName(typeName);
                setDirModalOpened(opened);
              }}
            />
          );
        })}
      </Stack>
      <ModelDirModal
        opened={dirModalOpened}
        modelType={currentModelTypeName}
        onClose={() => setDirModalOpened(false)}
      />
      <OtherUIDirModal
        opened={otherUIDirModalOpened}
        onClose={() => setOtherUIDirModelOpened(false)}
      />
      {civitVersionInfo && (
        <AddCivitAIModelModal
          opened={addModelOpened}
          civitModelVersion={civitVersionInfo}
          onClose={() => {
            setAddModelOpened(false);
          }}
          onFileToDownloadChanged={(allFilesToDownload) => {
            setFilesToDownload(allFilesToDownload);
          }}
          onDownload={() => {
            setAddModelOpened(false);
          }}
        />
      )}
    </ModelDownloadingContextProvider>
  );
}
