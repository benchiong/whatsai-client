import { useRouter } from "next/router";
import Head from "next/head";
import React, { useEffect, useState } from "react";
import { ModelInfoType } from "../../data-type/model";
import { getModelByModelLocalPath } from "../../lib/api";
import {
  Center,
  Group,
  Stack,
  ScrollArea,
  TypographyStylesProvider,
  useMantineTheme,
} from "@mantine/core";
import { IconX } from "@tabler/icons-react";
import { ImageLocal } from "../../components/Image/ImageLocal";
import { displayNameOfModelInfo } from "../../data-type/helpers";
import { ModelDetailInfo } from "../../components/Model/ModelDetailInfo";

export default function ModelDetail() {
  const theme = useMantineTheme();

  const router = useRouter();
  const [model, setModel] = useState<ModelInfoType | null>(null);

  useEffect(() => {
    const localPath = router.query.localPath;
    if (!localPath) {
      return;
    }

    if (Array.isArray(localPath)) {
      return;
    }
    getModelByModelLocalPath(localPath)
      .then((model) => setModel(model))
      .catch((e) => console.error(e));
  }, [router.query]);

  if (!model) {
    return <></>;
  }

  return (
    <TypographyStylesProvider>
      <Head>
        <title>{`Model: ${displayNameOfModelInfo(model)}`}</title>
      </Head>
      <Group
        style={{
          position: "relative",
        }}
        align={"start"}
      >
        <Center m={40} bg={theme.colors.waLight[1]}>
          <ImageLocal
            localPath={model.image_path}
            width={450}
            height={600}
            objectFit={"contain"}
          />
        </Center>

        <Stack style={{ position: "relative" }}>
          <ScrollArea
            scrollbars="y"
            scrollbarSize={2}
            bg={theme.colors.waLight[2]}
            h={`calc(100vh)`}
            w={600}
          >
            <ModelDetailInfo model={model} />
          </ScrollArea>

          <Center
            bg={theme.colors.waLight[4]}
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "25px",
              cursor: "pointer",
              position: "absolute",
              right: "-100px",
              top: "10px",
              zIndex: 400,
            }}
            onClick={() => {
              router.back();
            }}
          >
            <IconX />
          </Center>
        </Stack>
      </Group>
    </TypographyStylesProvider>
  );
}
