import {
  ScrollArea,
  Group,
  Stack,
  Text,
  Divider,
  useMantineTheme,
  Button,
  Center,
} from "@mantine/core";
import React, { useState } from "react";
import { CardInfoType } from "../../data-type/card";
import { AddonList } from "../Addon/AddonList";
import { useModelSelectionDrawerContext } from "../../providers/ModelSelectionDrawerProvider";
import { MODELS_DRAWER_HEIGHT } from "../../extras/constants";
import { WidgetsRender } from "../Widgets/WidgetsRender";
import { generate } from "../../lib/api";
import { useClientIdContext } from "../../providers/ClientIdProvider";
import { IconReload } from "@tabler/icons-react";
import { useCardContext } from "../../providers/CardProvider";
import { useTasksContext } from "../../providers/TasksProvider";
import { showErrorNotification } from "../../utils/notifications";

export function WACard({
  cardInfo,
  onCardInfoChanged,
  onReset,
  width = 470,
}: {
  cardInfo: CardInfoType;
  onCardInfoChanged: (cardInfo: CardInfoType) => void;
  onReset: () => void;
  width?: number;
}) {
  /*
    The core idea here is: we got a dict from backend, then parse it to dynamic render Widgets, after user
    make choices, return modified inputs to backend to generate.
   */
  const theme = useMantineTheme();
  const modelDrawerContext = useModelSelectionDrawerContext();
  const clientIdContext = useClientIdContext();
  const cardContext = useCardContext();
  const taskContext = useTasksContext();

  const [loading, setLoading] = useState(false);

  // Scroll Area height changes when drawer toggles opened/closed
  const height = modelDrawerContext.drawerOpened
    ? `calc(100vh - ${MODELS_DRAWER_HEIGHT}px - 60px)`
    : "calc(100vh - 60px)";

  const addons = cardInfo.addons;
  const hasAddons = addons && addons.length > 0; // Used to layout.

  return (
    <Group
      w={hasAddons ? 580 : 500}
      bg={theme.colors.waLight[1]}
      align={"start"}
      m={0}
      style={{
        position: "relative",
      }}
    >
      <Stack
        gap={0}
        w={"100%"}
        bg={theme.colors.waLight[1]}
        style={{
          position: "sticky",
          top: "0px",
          zIndex: "400",
        }}
      >
        <Group w={"100%"} justify={"space-between"} px={20}>
          <Text
            style={{
              textAlign: "center",
              lineHeight: "40px",
              height: "40px",
            }}
          >
            {cardInfo?.card_display_name ?? cardInfo?.card_name}
          </Text>

          <Center
            style={{
              position: "absolute",
              bottom: "10px",
              right: "10px",
              zIndex: 450,
            }}
            onClick={onReset}
          >
            <IconReload
              style={{
                color: "var(--mantine-color-waLight-9)",
                cursor: "pointer",
                height: "14px",
                width: "14px",
                strokeWidth: "1px",
              }}
            />
            <Text
              style={{
                fontSize: "12px",
                fontWeight: "300",
                cursor: "pointer",
              }}
              ml={5}
            >
              Reset
            </Text>
          </Center>
        </Group>

        <Divider color={theme.colors.waLight[3]} m={0} />
      </Stack>

      <ScrollArea
        w={width}
        h={height}
        style={{ transition: "height 0.3s ease" }}
        scrollbars="y"
        scrollbarSize={2}
        ml={25}
        mr={20}
        pb={80}
      >
        <WidgetsRender
          width={440}
          widgets={cardInfo.widgets}
          onChange={(widgets) => {
            const newCard = { ...cardInfo };
            newCard.widgets = widgets;
            onCardInfoChanged(newCard);
          }}
        />
      </ScrollArea>

      <AddonList cardInfo={cardInfo} onCardInfoChanged={onCardInfoChanged} />
      <Center
        bg={theme.colors.waLight[3]}
        w={"100%"}
        h={60}
        style={{
          position: "absolute",
          bottom: "0px",
          zIndex: "400",
        }}
      >
        <Button
          h={32}
          w={160}
          loading={loading}
          onClick={() => {
            setLoading(true);
            generate(cardInfo.card_name, clientIdContext.clientId)
              .then((r) => {
                setLoading(false);
                if (r) {
                  taskContext.startLoop();
                } else {
                  showErrorNotification({
                    error: Error("Generate error"),
                    reason: "Generate error",
                  });
                }
              })
              .catch((e) => {
                setLoading(false);

                showErrorNotification({
                  error: Error(e),
                  reason: e.toString(),
                });
              });
            cardContext.onGenerate();
            taskContext.setDrawerOpened(true);
          }}
        >
          Generate
        </Button>
      </Center>
    </Group>
  );
}
