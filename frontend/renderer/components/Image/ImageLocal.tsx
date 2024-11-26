import Image from "next/image";
import { localFile } from "../../lib/api";
import { useEffect, useState } from "react";
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
  const [imageUrl, setImageUrl] = useState("");
  const placeHolder = "/images/place-holder.png";
  useEffect(() => {
    if (!localPath) {
      setImageUrl(placeHolder);
      return;
    }
    localFile(localPath)
      .then((blob) => {
        if (blob) {
          const objectURL = URL.createObjectURL(blob);
          setImageUrl(objectURL);
        } else {
          setImageUrl(placeHolder);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        setImageUrl(placeHolder);
      });
  }, [localPath]);

  const src = imageUrl.startsWith("blob") ? imageUrl : placeHolder;

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
