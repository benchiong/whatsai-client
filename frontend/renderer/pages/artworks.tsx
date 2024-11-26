import React, { useCallback, useEffect, useState } from "react";
import Head from "next/head";
import { Group, Stack, useMantineTheme } from "@mantine/core";
import { ArtworkArrayType } from "../data-type/artwork";
import { ImageLocal } from "../components/Image/ImageLocal";
import { getArtworks } from "../lib/api";
import { useRouter } from "next/router";

export default function ArtworksPage() {
  const theme = useMantineTheme();

  const router = useRouter();
  const [arts, setArts] = useState<ArtworkArrayType>([]);

  const getAllArts = useCallback(() => {
    getArtworks()
      .then((arts) => {
        setArts(arts);
      })
      .catch((e) => {});
  }, []);

  useEffect(() => {
    getAllArts();
  }, []);

  return (
    <>
      <Head>
        <title>Artworks</title>
      </Head>
      <Group align={"start"} p={30} gap={30} flex={1}>
        {arts.map((artwork, index) => {
          return (
            <Stack
              w={270}
              h={360}
              bg={theme.colors.waLight[1]}
              style={{
                cursor: "pointer",
              }}
              onClick={() => {
                router.push(`/artwork-detail/${artwork.artwork_id}`);
              }}
            >
              <ImageLocal
                localPath={artwork.path}
                width={270}
                height={360}
                objectFit={"contain"}
              />
            </Stack>
          );
        })}
      </Group>
    </>
  );
}
