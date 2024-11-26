import React, { useEffect, useState } from "react";
import Head from "next/head";
import { Container, Group } from "@mantine/core";
import { SimpleCardInfoType } from "../data-type/card";
import { getAllCards } from "../lib/api";
import { CardDigest } from "../components/Card/CardDigest";

export default function HomePage() {
  const [cards, setCards] = useState<SimpleCardInfoType[]>([]);
  useEffect(() => {
    getAllCards().then((cards) => setCards(cards));
  }, []);

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
