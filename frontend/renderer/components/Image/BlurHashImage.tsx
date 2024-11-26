import { AspectRatio, Image, useMantineTheme } from "@mantine/core";
import { ImageHash } from "./ImageHash";
export function BlurHashImage({
  src,
  alt,
  hash,
  width,
  height,
}: {
  src?: string;
  alt?: string;
  hash?: string;
  width: number;
  height: number;
}) {
  const theme = useMantineTheme();

  if (!src || !alt || !hash) {
    return <></>;
  }

  return (
    <AspectRatio
      ratio={width / height}
      w={width}
      h={height}
      bg={theme.colors.waLight[2]}
      style={{
        borderRadius: "10px",
        overflow: "hidden",
        position: "relative",
      }}
    >
      <Image
        src={src}
        alt={alt}
        style={{
          zIndex: 200,
          position: "absolute",
          top: "0px",
          left: "0px",
        }}
      />
      <ImageHash hash={hash} width={width} height={height} />
    </AspectRatio>
  );
}
