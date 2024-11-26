import { SimpleCardInfoType } from "../../data-type/card";
import { Stack, useMantineTheme, Image, Text, Center } from "@mantine/core";
import { ImageLocal } from "../Image/ImageLocal";
import { useRouter } from "next/router";

export function CardDigest({ simpleCard }: { simpleCard: SimpleCardInfoType }) {
  const theme = useMantineTheme();
  const router = useRouter();
  return (
    <Stack
      bg={theme.colors.waLight[3]}
      m={0}
      gap={20}
      h={360}
      w={210}
      align={"center"}
      style={{
        borderRadius: "20px",
        overflow: "hidden",
        cursor: "pointer",
      }}
      onClick={() => {
        router.push(`/card-detail/${simpleCard.card_name}`);
      }}
    >
      {simpleCard.cover_image &&
        (simpleCard.cover_image.startsWith("http") ? (
          <Center w={210} h={280}>
            <Image src={simpleCard.cover_image} w={210} h={280} />
          </Center>
        ) : (
          <ImageLocal
            localPath={simpleCard.cover_image}
            width={210}
            height={280}
          />
        ))}
      <Text
        w={"100%"}
        lineClamp={2}
        px={10}
        style={{
          textAlign: "center",
          fontWeight: 400,
          fontSize: "16px",
          wordBreak: "break-word",
        }}
      >
        {simpleCard.card_name}
      </Text>
    </Stack>
  );
}
