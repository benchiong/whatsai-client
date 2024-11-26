import { AddonType } from "../../data-type/addons";
import { useModelSelectionDrawerContext } from "../../providers/ModelSelectionDrawerProvider";
import React from "react";
import { MODELS_DRAWER_HEIGHT } from "../../extras/constants";
import { CardInfoType } from "../../data-type/card";
import { Center, ScrollArea, Stack } from "@mantine/core";
import { Close } from "../Widgets/Close";
import { Addon } from "./Addon";

export function AddonPopover({
  cardInfo,
  addonIndex,
  closeAddon,
  onAddonChanged,
}: {
  cardInfo: CardInfoType;
  addonIndex: number;
  closeAddon: () => void;
  onAddonChanged: (changedAddon: AddonType) => void;
}) {
  const modelDrawerContext = useModelSelectionDrawerContext();
  const height = modelDrawerContext.drawerOpened
    ? `calc(100vh - ${MODELS_DRAWER_HEIGHT + 100}px)`
    : "calc(100vh - 100px)";

  return (
    <Stack
      style={{
        position: "relative",
      }}
    >
      <Center
        style={{
          position: "absolute",
          top: "3px",
          right: "3px",
          zIndex: 450,
        }}
      >
        <Close onClick={closeAddon} width={20} />
      </Center>

      <ScrollArea
        w={400}
        h={height}
        style={{ transition: "height 0.3s ease" }}
        scrollbars="y"
        scrollbarSize={2}
        m={0}
      >
        {addonIndex !== -1 && (
          <Addon
            cardInfo={cardInfo}
            addonIndex={addonIndex}
            key={addonIndex}
            onAddonChanged={onAddonChanged}
            closeAddon={closeAddon}
          />
        )}
      </ScrollArea>
    </Stack>
  );
}
