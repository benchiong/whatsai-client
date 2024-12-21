import Image from "next/image";
import { ObjectFit } from "../helpers";

export function ImageLocal({
  localPath,
  width,
  height,
  objectFit = "cover",
}: {
  localPath: string | null;
  width: number;
  height: number;
  objectFit?: ObjectFit;
}) {
  const placeHolder = "/images/place-holder.png";
  const src = localPath ? `file://${localPath}` : placeHolder;

  return (
    <Image
      src={src}
      alt={"local image"}
      width={width}
      height={height}
      style={{
        objectFit: objectFit,
        borderRadius: "5px",
      }}
      key={localPath}
    />
  );
}
