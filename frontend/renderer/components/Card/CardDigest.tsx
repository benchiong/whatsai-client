import { SimpleCardInfoType } from "../../data-type/card";
import { Stack, useMantineTheme, Text, Center } from "@mantine/core";
import Image from "next/image";

import { ImageLocal } from "../Image/ImageLocal";
import { useRouter } from "next/router";

export function CardDigest({ simpleCard }: { simpleCard: SimpleCardInfoType }) {
  const theme = useMantineTheme();
  const router = useRouter();
  return (
    <Stack
      bg={theme.colors.waLight[3]}
      m={0}
      gap={0}
      p0
      h={250}
      w={160}
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
          <Center w={160} h={200}>
            <Image
              src={simpleCard.cover_image}
              width={160}
              height={200}
              alt={"image"}
              style={{
                objectFit: "cover",
                borderRadius: "5px",
              }}
            />
          </Center>
        ) : (
          <ImageLocal
            localPath={simpleCard.cover_image}
            width={160}
            height={200}
          />
        ))}
      <Center h={40}>
        <Text
          w={"100%"}
          lineClamp={2}
          mt={5}
          px={5}
          style={{
            textAlign: "center",
            fontWeight: 500,
            fontSize: "14px",
            wordBreak: "break-word",
          }}
        >
          {simpleCard.display_name}
        </Text>
      </Center>
    </Stack>
  );
}
