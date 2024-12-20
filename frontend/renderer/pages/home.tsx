import React, { useEffect, useState } from "react";
import Head from "next/head";
import { Container, Group } from "@mantine/core";
import { SimpleCardInfoType } from "../data-type/card";
import { getAllCards } from "../lib/api";
import { CardDigest } from "../components/Card/CardDigest";
import { useBackendManagerContext } from "../providers/BackendManagerProvider";

export default function HomePage() {
  const [cards, setCards] = useState<SimpleCardInfoType[]>([]);
  const backendManagerContext = useBackendManagerContext();
  useEffect(() => {
    if (!backendManagerContext.isBackendReady) {
      return;
    }
    getAllCards()
      .then((cards) => setCards(cards))
      .catch((e) => {
        console.log("getAllCards error:", e);
      });
  }, [backendManagerContext.isBackendReady]);

  return (
    <>
      <Head>
        <title>Cards</title>
      </Head>
      <Group align={"start"} p={30} gap={30} flex={1}>
        {cards.map((card, index) => (
          <CardDigest simpleCard={card} key={index} />
        ))}
      </Group>
    </>
  );
}
