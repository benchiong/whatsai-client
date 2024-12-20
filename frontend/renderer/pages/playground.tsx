import React, { useState } from "react";
import Head from "next/head";
import {
  Center,
  Box,
  Stack,
  useMantineTheme,
  Button,
  Container,
  Image,
  useMantineColorScheme,
} from "@mantine/core";
import {
  home,
  getCardInfo,
  localFile,
  widget,
  listModels,
  getAddonWidgetInfos,
  getRecentlyUsed,
  addRecentlyUsed,
  execute,
  getAllCards,
  updateCardCache,
  generate,
  getTasks,
  removeTask,
  getArtworks,
  getModels,
  getModelDir,
  isDirOk,
  addOtherUIDirs,
  getCivitaiModelVersionInfo,
  getDownloadingInfos,
  getArtwork,
} from "../lib/api";
import { showNormalNotification } from "../utils/notifications";

import { atom, useRecoilState } from "recoil";
import { useClientIdContext } from "../providers/ClientIdProvider";
import { useTasksContext } from "../providers/TasksProvider";
import { backendManager } from "../../main/ipc-constants";
import { eventBackendManagerUrl } from "../../main/ipc-constants";

export default function HomePage() {
  const theme = useMantineTheme();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const clientIdContext = useClientIdContext();
  const task = useTasksContext().tasks[0];

  const fontSizeState = atom({
    key: "fontSizeState",
    default: 14,
  });
  const [fontSize, setFontSize] = useRecoilState(fontSizeState);

  return (
    <>
      <Head>
        <title>Play Ground</title>
      </Head>
      <Container>
        Home Page
        <Stack maw={400} bg="var(--mantine-color-gray-light)">
          <Button
            onClick={() => {
              const res = home().then((r) => console.log(r));
            }}
          >
            test request
          </Button>
          <Button
            onClick={() => {
              const res = widget().then((r) => console.log(r));
            }}
          >
            test widget
          </Button>
          <Button
            onClick={() => {
              const res = getCardInfo(
                "TEST-Stable-Diffusion-Text-to-Image",
              ).then((r) => console.log(r));
            }}
          >
            test card info
          </Button>
          <Button
            onClick={() => {
              const res = localFile(
                "/Users/ben/whatsai/model_infos/images/v1-5-pruned-emaonly.safetensors.jpeg",
              ).then((r) => console.log(r));
            }}
          >
            localFile
          </Button>
          <Button
            onClick={() => {
              listModels("list_checkpoints").then((result) => {
                console.log(result);
              });
            }}
          >
            widgetFunction
          </Button>
          <Button
            onClick={() => {
              showNormalNotification({
                title: "Model unavailable.",
                message: "You can use it after downloading.",
              });
              // showErrorNotification({
              //   error: new Error("errorMessage"),
              // });
              return;
            }}
          >
            notificaiton
          </Button>
          <Button onClick={() => toggleColorScheme()}>Dark/Light</Button>
          <Button
            onClick={() =>
              getAddonWidgetInfos("LoRA").then((r) => {
                console.log(r);
              })
            }
          >
            Addon Widgets
          </Button>
          <Button onClick={() => setFontSize((size) => size + 1)}>
            {`recoil test ${fontSize}`}
          </Button>
          <Button
            onClick={() => {
              getRecentlyUsed("image", "")
                .then((r) => console.log(r))
                .catch((e) => {
                  console.log(e);
                });
            }}
          >
            getRecentlyUsed
          </Button>
          <Button
            onClick={() => {
              addRecentlyUsed(
                "image",
                "controlnet",
                "/Users/ben/whatsai/output/images/20240929-133746.png",
              )
                .then((r) => console.log(r))
                .catch((e) => {
                  console.log(e);
                });
            }}
          >
            addRecentlyUsed
          </Button>
          <Button
            onClick={() => {
              getAllCards()
                .then((cards) => console.log(cards))
                .catch((e) => {
                  console.log(e);
                });
            }}
          >
            Get All cards
          </Button>
          <Button
            onClick={() => {
              removeTask(26).then((r) => {
                console.log(r);
              });
            }}
          >
            removeTask
          </Button>
          <Button
            onClick={() => {
              removeTask(26).then((r) => {
                console.log(r);
              });
            }}
          >
            removeTask
          </Button>

          <Button
            onClick={() => {
              getModels().then((r) => {
                console.log(r);
              });
            }}
          >
            getModels
          </Button>
          <Button
            onClick={() => {
              isDirOk("/").then((r) => {
                console.log(r);
              });
            }}
          >
            getModelDir
          </Button>
          <Button
            onClick={() => {
              addOtherUIDirs(
                "WebUI",
                "/Volumes/Storage/stable-diffusion-webui-newer/",
              ).then((resp) => console.log(resp));
            }}
          >
            AddOtherUIDirs
          </Button>
          <Button
            onClick={() => {
              const url = "https://civitai.com/models/9139/checkpointyesmix";
              getCivitaiModelVersionInfo(url).then((r) => console.log(r));
            }}
          >
            Test civitai model info
          </Button>
          <Button
            onClick={() => {
              getDownloadingInfos().then((r) => console.log(r));
            }}
          >
            getDownloadingInfos{" "}
          </Button>

          <Button
            onClick={() => {
              getArtwork(10000).then((r) => console.log(r));
            }}
          >
            getArtwork
          </Button>
        </Stack>
      </Container>
    </>
  );
}
