import {
  Stack,
  Group,
  Text,
  Button,
  useMantineTheme,
  Center,
} from "@mantine/core";
import { ModelInfoType } from "../../data-type/model";
import { LabelSingleLine } from "./LabelSingleLine";
import { ImageLocal } from "../Image/ImageLocal";
import { ModelDetailInfoCard } from "./ModelDetailInfoCard";
import { Close } from "./Close";
import React, { useEffect, useState } from "react";
import { IconInfoSquareRounded } from "@tabler/icons-react";
import { useModelSelectionDrawerContext } from "../../providers/ModelSelectionDrawerProvider";
import { displayNameOfModelInfo } from "../../data-type/helpers";
import { getModelByModelId } from "../../lib/api";

export function WidgetModelCombo({
  text,
  defaultModelId = null,
  funcName = "",
  paramName = "",
  width = "100%",
  optional = false,
  onChange,
  positionIndex = null,
}: {
  text: string;
  defaultModelId: string | null;
  width?: number | string;
  funcName?: string;
  paramName?: string;
  optional?: boolean;
  onChange?: (value: string | null) => void;
  positionIndex?: number | null;
}) {
  const theme = useMantineTheme();
  const [overLayVisible, setOverlayVisible] = useState(false);
  const [detailOpened, setDetailOpened] = useState(false);

  const _text = positionIndex ? `${text} - ${positionIndex}` : text;

  const [model, setModel] = useState<ModelInfoType | null>(null);
  const modelDrawerContext = useModelSelectionDrawerContext();

  useEffect(() => {
    if (!defaultModelId) {
      setModel(null);
    }
    getModelByModelId(defaultModelId!)
      .then((model) => setModel(model))
      .catch((e) => console.error(e));
  }, []);

  const toggleDrawer = () => {
    modelDrawerContext.toggleDrawer(_text, funcName, paramName, (model) => {
      setModel(model);
      onChange && onChange(model.file_name);
    });
  };

  const activate =
    modelDrawerContext.drawerOpened && modelDrawerContext.displayName === _text;

  return (
    <Stack
      justify={"start"}
      style={{
        borderRadius: `10px`,
        cursor: "pointer",
        position: "relative",
        border: activate
          ? "0.5px solid var(--mantine-color-primary-5)"
          : "none",
      }}
      w={width}
      miw={220}
      mih={170}
      bg={theme.colors.waLight[3]}
    >
      <LabelSingleLine text={text} />
      {model ? (
        <ModelDetailInfoCard
          model={model}
          opened={detailOpened}
          close={() => setDetailOpened(false)}
        >
          <Group mb={10} mx={20}>
            <Stack
              style={{
                position: "relative",
              }}
              onMouseEnter={() => setOverlayVisible(true)}
              onMouseLeave={() => setOverlayVisible(false)}
            >
              <ImageLocal
                localPath={model.image_path ?? ""}
                width={70}
                height={105}
                key={text}
              />
              {overLayVisible && (
                <IconInfoSquareRounded
                  style={{
                    position: "absolute",
                    left: "2px",
                    top: "2px",
                    color: "var(--mantine-color-primary-3)",
                    cursor: "pointer",
                    height: "18px",
                    width: "18px",
                    strokeWidth: "1px",
                    zIndex: 401,
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    setDetailOpened(!detailOpened);
                  }}
                />
              )}
            </Stack>

            <Stack flex={1} h={"100%"} justify={"start"} gap={10}>
              <Text
                lineClamp={2}
                style={{
                  fontSize: "12px",
                  fontWeight: "500",
                  wordBreak: "break-all",
                }}
              >{`${displayNameOfModelInfo(model)}`}</Text>

              <Text
                c={theme.colors.waLight[8]}
                style={{
                  fontSize: "12px",
                  fontWeight: "500",
                }}
              >{`Base Model:   ${model.civit_model?.baseModel ?? " - "}`}</Text>
              <Button
                onClick={() => toggleDrawer()}
                style={{
                  fontWeight: 600,
                  fontSize: 12,
                  backgroundColor: "var(--mantine-color-waLight-4)",
                  color: "var(--mantine-color-primary-3)",
                }}
                w={100}
                h={26}
              >
                Select
              </Button>
            </Stack>
          </Group>
        </ModelDetailInfoCard>
      ) : (
        <Center mb={20} flex={1} w={"100%"}>
          <Button
            onClick={() => {
              toggleDrawer();
            }}
            style={{
              fontWeight: 600,
              fontSize: 12,
              backgroundColor: "var(--mantine-color-waLight-4)",
              color: "var(--mantine-color-phOrange-1)",
            }}
            h={26}
          >
            {`Select ${text}`}
          </Button>
        </Center>
      )}

      {optional && model && (
        <Center
          style={{
            position: "absolute",
            top: "15px",
            right: "15px",
          }}
        >
          <Close
            width={20}
            height={20}
            onClick={() => {
              setModel(null);
              onChange && onChange(null);
            }}
          />
        </Center>
      )}
    </Stack>
  );
}
