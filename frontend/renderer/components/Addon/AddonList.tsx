import { Popover, Stack, useMantineTheme } from "@mantine/core";
import React, { useState } from "react";
import { useModelSelectionDrawerContext } from "../../providers/ModelSelectionDrawerProvider";
import { AddonListType, CardInfoType } from "../../data-type/card";
import { AddonPopover } from "./AddonPopover";
import { AddonTabItem } from "./AddonTabItem";

export function AddonList({ cardInfo }: { cardInfo: CardInfoType }) {
  const theme = useMantineTheme();
  const modelDrawerContext = useModelSelectionDrawerContext();

  const [addons, setAddons] = useState<AddonListType>(cardInfo.addons);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);
  const closeAddon = () => {
    setSelectedIndex(-1);
    modelDrawerContext.setDrawerOpened(false);
  };

  const customColors = [
    theme.colors.customBlue[0],
    theme.colors.customPurple[0],
    theme.colors.customGreen[0],
    theme.colors.customYellow[0],
    theme.colors.customPink[0],
  ];

  return (
    <Popover
      width={200}
      position="right"
      opened={!(selectedIndex == -1)}
      shadow={"md"}
    >
      <Popover.Target>
        <Stack
          w={60}
          mt={15}
          style={{
            position: "absolute",
            right: "0px",
            top: "40px", // height of card title.
          }}
          gap={20}
        >
          {addons.map((addon, index) => {
            return (
              <AddonTabItem
                key={addon.display_name}
                addon={addon}
                addonIndex={index}
                bg={customColors[index % customColors.length]}
                selected={selectedIndex == index}
                onClick={(idx) => {
                  if (idx == selectedIndex) {
                    setSelectedIndex(-1);
                    modelDrawerContext.setDrawerOpened(false);
                  } else {
                    setSelectedIndex(index);
                  }
                }}
              />
            );
          })}
        </Stack>
      </Popover.Target>
      <Popover.Dropdown
        w={400}
        bg={theme.colors.waLight[5]}
        style={{
          position: "absolute",
          top: "40px",
          borderRadius: "5px",
          border: "none",
          padding: "0px",
        }}
      >
        <AddonPopover
          cardInfo={cardInfo}
          addonIndex={selectedIndex}
          key={selectedIndex}
          closeAddon={closeAddon}
          onAddonChanged={(changedAddon) => {
            const newAddons = [...addons];
            newAddons[selectedIndex] = changedAddon;
            setAddons(newAddons);
          }}
        />
      </Popover.Dropdown>
    </Popover>
  );
}
