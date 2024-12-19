import {
  MODELS_DRAWER_HEIGHT,
  NAV_WIDTH,
  TASK_DRAWER_WIDTH,
} from "../../extras/constants";
import {
  Center,
  Drawer,
  Group,
  Overlay,
  ScrollArea,
  Stack,
  Text,
  useMantineTheme,
} from "@mantine/core";
import { Refresh } from "../Widgets/Refresh";
import { Close } from "../Widgets/Close";
import React, { useState } from "react";
import {
  ModelInfoArrayType,
  ModelInfoListType,
  ModelInfoType,
} from "../../data-type/model";
import { ImageLocal } from "../Image/ImageLocal";
import { ModelDetailInfoCard } from "../Widgets/ModelDetailInfoCard";
import { IconInfoSquareRounded } from "@tabler/icons-react";
import { useTasksContext } from "../../providers/TasksProvider";
import { displayNameOfModelInfo } from "../../data-type/helpers";

export function ModelComboDrawer({
  drawerOpened,
  closeDrawer,
  modelType,
  onModelSelected,
  models,
  refreshModels,
}: {
  drawerOpened: boolean;
  closeDrawer: () => void;
  modelType: string;
  onModelSelected: (model: ModelInfoType) => void;
  models: ModelInfoListType;
  refreshModels: () => Promise<void>;
}) {
  const theme = useMantineTheme();
  const tasksContext = useTasksContext();
  const width = tasksContext.drawerOpened
    ? `calc(100vw - ${NAV_WIDTH}px - ${TASK_DRAWER_WIDTH}px`
    : `calc(100vw - ${NAV_WIDTH}px`;

  return (
    <Drawer
      lockScroll={false}
      zIndex={100}
      opened={drawerOpened}
      position={"bottom"}
      onClose={() => {}}
      withOverlay={false}
      shadow={"lg"}
      size={`${MODELS_DRAWER_HEIGHT}px`}
      withCloseButton={false}
      transitionProps={{ duration: 300, timingFunction: "const" }}
      styles={{
        inner: {
          marginLeft: `${NAV_WIDTH}px`,
          marginRight: "300px",
        },
        content: {
          backgroundColor: `var(--mantine-color-waLight-1)`,
        },
        body: {
          padding: "0px",
        },
      }}
    >
      <Stack gap={0} w={width}>
        <Group
          h={44}
          px={20}
          bg={theme.colors.waLight[2]}
          justify={"space-between"}
        >
          <Group>
            <Text
              h={30}
              mr={10}
              style={{
                lineHeight: "30px",
                userSelect: "none",
              }}
            >
              {`Select ${modelType}`}
            </Text>
            <Refresh asyncOperation={refreshModels} />
          </Group>

          <Close onClick={() => closeDrawer()} />
        </Group>

        <ScrollArea h={MODELS_DRAWER_HEIGHT - 44} w={width}>
          <Group mx={20} pt={20} pb={50}>
            {models &&
              models.map((model) => {
                return (
                  <ModelInfoItem
                    key={model.local_path}
                    model={model}
                    onClick={() => {
                      onModelSelected(model);
                    }}
                  />
                );
              })}
          </Group>
        </ScrollArea>
      </Stack>
    </Drawer>
  );
}

function ModelInfoItem({
  model,
  onClick,
}: {
  model: ModelInfoType;
  onClick: () => void;
}) {
  const theme = useMantineTheme();

  const [detailOpened, setDetailOpened] = useState(false);
  const [overLayVisible, setOverlayVisible] = useState(false);

  return (
    <Stack
      justify={"center"}
      align={"center"}
      w={160}
      style={{
        cursor: "pointer",
      }}
      onClick={onClick}
    >
      <ModelDetailInfoCard
        model={model}
        opened={detailOpened}
        close={() => setDetailOpened(false)}
      >
        <Stack>
          <Center
            w={140}
            h={210}
            pos="relative"
            onMouseEnter={() => setOverlayVisible(true)}
            onMouseLeave={() => setOverlayVisible(false)}
          >
            <ImageLocal
              localPath={model.image_path ?? ""}
              width={140}
              height={210}
            />

            {overLayVisible && (
              <>
                <IconInfoSquareRounded
                  style={{
                    position: "absolute",
                    left: "5px",
                    top: "5px",
                    color: "var(--mantine-color-primary-1)",
                    cursor: "pointer",
                    height: "22px",
                    width: "22px",
                    strokeWidth: "1px",
                    zIndex: 401,
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    setDetailOpened(!detailOpened);
                  }}
                />
                <Overlay
                  color={theme.colors.waLight[0]}
                  backgroundOpacity={0.7}
                  radius={5}
                >
                  <Center w={"100%"} h={"100%"}>
                    <Text
                      w={80}
                      h={24}
                      c={theme.colors.waLight[5]}
                      bg={theme.colors.waDark[5]}
                      style={{
                        lineHeight: "24px",
                        borderRadius: "5px",
                        fontSize: "12px",
                        opacity: 0.7,
                        fontWeight: 500,
                        textAlign: "center",
                      }}
                    >
                      Select
                    </Text>
                  </Center>
                </Overlay>
              </>
            )}
          </Center>

          <Text
            lineClamp={2}
            h={40}
            style={{
              fontSize: "12px",
              fontWeight: "500",
              wordBreak: "break-all",
            }}
          >{`${displayNameOfModelInfo(model)}`}</Text>
        </Stack>
      </ModelDetailInfoCard>
    </Stack>
  );
}
