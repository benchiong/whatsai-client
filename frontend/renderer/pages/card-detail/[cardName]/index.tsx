import { Group, Center, useMantineTheme } from "@mantine/core";
import { useRouter } from "next/router";
import Head from "next/head";
import React, { useCallback, useEffect, useState } from "react";
import { IconX } from "@tabler/icons-react";
import { CardInfoType } from "../../../data-type/card";
import { getCardInfo, updateCardCache } from "../../../lib/api";
import { WACard } from "../../../components/Card/WACard";
import { ModelSelectionDrawerProvider } from "../../../providers/ModelSelectionDrawerProvider";
import { CardContextProvider } from "../../../providers/CardProvider";

export default function CardDetail() {
  const router = useRouter();
  const theme = useMantineTheme();

  const [cardInfo, setCardInfo] = useState<CardInfoType | null>(null);

  useEffect(() => {
    const { cardName } = router.query;
    if (!cardName) {
      return;
    }
    if (Array.isArray(cardName)) {
      return;
    }
    getCardInfo(cardName).then((resp) => {
      setCardInfo(resp.cardInfo);
    });
  }, [router.query]);

  const onCardInfoChanged = useCallback(
    (changedInfo: CardInfoType) => {
      if (!cardInfo) {
        return;
      }
      updateCardCache(cardInfo.card_name, changedInfo).then((r) => {});
    },
    [cardInfo],
  );

  const onReset = useCallback(() => {
    if (!cardInfo) {
      return;
    }
    const cardName = cardInfo.card_name;
    updateCardCache(cardName, {}).then((success) => {
      if (success) {
        getCardInfo(cardName).then((resp) => {
          setCardInfo(resp.cardInfo);
          router.back();
        });
      }
    });
  }, [cardInfo]);

  return (
    <CardContextProvider>
      <ModelSelectionDrawerProvider>
        <Head>
          <title>{`Card: ${cardInfo?.card_name}`}</title>
        </Head>
        <Group
          justify={"space-between"}
          align={"start"}
          bg={theme.colors.waLight[0]}
          gap={0}
          m={0}
          style={{
            position: "relative",
          }}
        >
          {cardInfo && (
            <WACard
              cardInfo={cardInfo}
              onCardInfoChanged={onCardInfoChanged}
              onReset={onReset}
            />
          )}

          <Center
            bg={theme.colors.waLight[4]}
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "25px",
              cursor: "pointer",
              position: "absolute",
              left: "650px",
              top: "10px",
              zIndex: 400,
            }}
            onClick={() => {
              router.back();
            }}
          >
            <IconX />
          </Center>
        </Group>
      </ModelSelectionDrawerProvider>
    </CardContextProvider>
  );
}
