import React, { useCallback, useEffect, useState } from "react";
import Head from "next/head";
import { Center, Group, Loader, Stack, useMantineTheme } from "@mantine/core";
import { useInViewport } from "@mantine/hooks";

import { ArtworkArrayType } from "../data-type/artwork";
import { ImageLocal } from "../components/Image/ImageLocal";
import { getArtworks } from "../lib/api";
import { useRouter } from "next/router";

export default function ArtworksPage() {
  const theme = useMantineTheme();

  const router = useRouter();
  const { ref, inViewport } = useInViewport();
  const [artworks, setArtworks] = useState<ArtworkArrayType>([]);
  const [pageNumber, setPageNumber] = useState<number>(0);
  const [hasNext, setHasNext] = useState(true);
  const [loading, setLoading] = useState(false);

  const getPaginatedArtworks = useCallback((pageNumber: number) => {
    setLoading(true);
    getArtworks(pageNumber)
      .then((artworkResponse) => {
        setLoading(false);
        if (artworkResponse) {
          const newArtworks = artworkResponse.artworks;
          setArtworks((prevArtworks) => [...prevArtworks, ...newArtworks]);
          setPageNumber(artworkResponse.page_num + 1);
          setHasNext(artworkResponse.has_next);
        }
      })
      .catch((e) => {
        setLoading(false);
        console.log(e);
      });
  }, []);

  useEffect(() => {
    getPaginatedArtworks(0);
  }, []);

  useEffect(() => {
    if (hasNext && inViewport && !loading) {
      getPaginatedArtworks(pageNumber);
    }
  }, [hasNext, inViewport, pageNumber, loading]);

  return (
    <>
      <Head>
        <title>Artworks</title>
      </Head>
      <Stack>
        <Group align={"start"} p={30} gap={30} flex={1}>
          {artworks.map((artwork, index) => {
            return (
              <Stack
                width={180}
                height={240}
                bg={theme.colors.waLight[1]}
                style={{
                  cursor: "pointer",
                }}
                onClick={() => {
                  router.push(`/artwork-detail/${artwork.id}`);
                }}
                key={artwork.id}
              >
                <ImageLocal
                  localPath={artwork.thumb?.file_path ?? artwork.file_path}
                  width={180}
                  height={240}
                  objectFit={"contain"}
                />
              </Stack>
            );
          })}
        </Group>
        <Center w={"100%"} ref={ref}>
          {loading && <Loader color={theme.colors.primary[0]} size={"12px"} />}
        </Center>
      </Stack>
    </>
  );
}
