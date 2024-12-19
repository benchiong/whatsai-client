import { Center, Image, Overlay } from "@mantine/core";
import React from "react";

export default function SlashPage() {
  return (
    <Overlay
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        backgroundColor: "var(--mantine-color-waLight-0)",
        zIndex: 9999,
      }}
    >
      <Center h={"100%"} w={"100%"}>
        <Image src={"/images/logo.png"} w={100} h={100} />
      </Center>
    </Overlay>
  );
}

SlashPage.getLayout = () => {};
