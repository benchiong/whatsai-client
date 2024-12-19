import { Stack } from "@mantine/core";
import React from "react";
import { ArtworkType } from "../../data-type/artwork";
import { ParamItem } from "./ParamItem";

export function ArtworkInfo({ artwork }: { artwork: ArtworkType }) {
  return (
    <Stack p={20}>
      <Stack>
        <ParamItem
          key={"file_path"}
          name={"file_path"}
          value={artwork.file_path}
        />

        {Object.entries(artwork.meta_info).map(([key, value]) => {
          if (value) {
            return <ParamItem key={key} name={key} value={value} />;
          }
        })}
      </Stack>
    </Stack>
  );
}
