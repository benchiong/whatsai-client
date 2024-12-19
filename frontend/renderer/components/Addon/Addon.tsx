import { AddonType } from "../../data-type/addons";
import { AddonTitle } from "./AddonTitle";
import React, { useCallback, useEffect, useState } from "react";
import {
  Button,
  Center,
  Chip,
  Stack,
  Text,
  useMantineTheme,
} from "@mantine/core";
import { WidgetsRender } from "../Widgets/WidgetsRender";
import { AddonListType, CardInfoType } from "../../data-type/card";
import { getCardInfo, updateCardCache } from "../../lib/api";
import { IconReload } from "@tabler/icons-react";

export function Addon({
  cardInfo,
  addonIndex,
  onAddonChanged,
  closeAddon,
}: {
  cardInfo: CardInfoType;
  addonIndex: number;
  onAddonChanged: (changedAddon: AddonType) => void;
  closeAddon: () => void;
}) {
  const theme = useMantineTheme();

  const [addon, setAddon] = useState<AddonType | null>(null);

  useEffect(() => {
    const cardName = cardInfo.card_name;

    getCardInfo(cardName).then((resp) => {
      const cardInfo = resp.cardInfo;
      if (cardInfo) {
        const addons = cardInfo.addons;
        const addon = addons[addonIndex];
        setAddon(addon);
      }
    });
  }, [cardInfo]);

  const innerOnAddonChanged = useCallback(
    (changedAddon: AddonType) => {
      const changedInfo = {
        ...cardInfo,
      };

      const changedAddons: AddonListType = [...changedInfo.addons];
      changedAddons[addonIndex] = changedAddon;
      changedInfo.addons = changedAddons;
      updateCardCache(cardInfo.card_name, changedInfo).then((resp) => {
        // if (resp?.cardInfo?.addons) {
        //   setAddon(resp.cardInfo!.addons!)
        // }
      });
      onAddonChanged(changedAddon);
    },
    [cardInfo],
  );

  return (
    <>
      {addon && (
        <Stack align={"center"}>
          <AddonTitle text={addon.display_name} />

          {addon.can_turn_off && (
            <Chip
              key={addon.addon_name}
              checked={!addon.is_off}
              onChange={() => {
                const newAddon: AddonType = { ...addon! };
                newAddon.is_off = !newAddon.is_off;
                setAddon(newAddon);
                innerOnAddonChanged(newAddon);
              }}
            >
              {!addon.is_off
                ? `Turn ${addon.addon_name} Off`
                : `Turn ${addon.addon_name} On`}
            </Chip>
          )}
          <Stack>
            {addon.widgets.map((_widgets, index) => {
              return (
                <Stack
                  bg={theme.colors.waLight[2]}
                  w={360}
                  px={15}
                  py={20}
                  gap={5}
                  style={{
                    borderRadius: "5px",
                    position: "relative",
                  }}
                  align={"center"}
                  key={index}
                >
                  <WidgetsRender
                    key={index}
                    positionIndex={index}
                    width={320}
                    widgets={_widgets}
                    onChange={(widgets) => {
                      const newAddon: AddonType = { ...addon! };
                      newAddon.widgets = [...newAddon.widgets];
                      newAddon.widgets[index] = widgets;
                      setAddon(newAddon);
                      innerOnAddonChanged(newAddon);
                    }}
                  />
                </Stack>
              );
            })}

            {addon.comp_list && (
              <Center mb={15}>
                <Button
                  hidden={true}
                  w={120}
                  h={26}
                  opacity={0.6}
                  onClick={() => {
                    const newAddon: AddonType = { ...addon! };
                    newAddon.widgets = [...addon!.widgets, addon!.comp_widgets];
                    setAddon(newAddon);
                    innerOnAddonChanged(newAddon);
                  }}
                  style={{
                    fontSize: "10px",
                  }}
                >
                  {`Add ${addon.addon_name}`}
                </Button>
              </Center>
            )}
          </Stack>

          <Center
            style={{
              position: "absolute",
              bottom: "10px",
              right: "10px",
              zIndex: 450,
            }}
            onClick={(e) => {
              e.stopPropagation();
              const newAddon: AddonType = { ...addon! };
              if (newAddon.can_turn_off) {
                newAddon.is_off = true;
              }
              newAddon.widgets = [newAddon.comp_widgets];
              setAddon(newAddon);
              innerOnAddonChanged(newAddon);
              closeAddon();
            }}
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
        </Stack>
      )}
    </>
  );
}
