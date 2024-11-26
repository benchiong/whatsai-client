import { ModelInfoListType, ModelsRecordType } from "../../data-type/model";
import { Stack, Group, Text, Center, useMantineTheme } from "@mantine/core";
import { capitalizeFirstLetter, getKeyOfModelsRecord } from "../../lib/utils";
import React, { useState } from "react";
import { ImageLocal } from "../Image/ImageLocal";
import { IconFolder } from "@tabler/icons-react";
import { displayNameOfModelInfo } from "../../data-type/helpers";
import { useRouter } from "next/router";
import { Refresh } from "../Widgets/Refresh";
import { syncModelInfos } from "../../lib/api";

export function ModelsRecord({
  modelsRecord,
  openDirModel,
}: {
  modelsRecord: ModelsRecordType;
  openDirModel: (opened: boolean, typeName: string) => void;
}) {
  const theme = useMantineTheme();
  const router = useRouter();

  const typeName = getKeyOfModelsRecord(modelsRecord);
  const DisplayTypeName = capitalizeFirstLetter(typeName);
  const defaultModels = modelsRecord[typeName];

  const [models, setModels] = useState<ModelInfoListType>(defaultModels);

  return (
    <Stack p={20}>
      <Group justify={"space-between"} h={36} bg={theme.colors.waLight[3]}>
        <Group>
          <Text
            c={theme.colors.waDark[3]}
            ml={20}
            style={{
              textAlign: "start",
              fontSize: "14px",
              fontWeight: 300,
              height: "30px",
              lineHeight: "30px",
              position: "sticky",
              top: "0px",
              zIndex: 100,
            }}
          >
            {DisplayTypeName}
          </Text>

          <Text
            span
            mr={10}
            px={8}
            py={2}
            style={{
              background: "var(--mantine-color-waLight-2)",
              borderRadius: "10px",
              fontSize: "12px",
              fontWeight: 300,
            }}
          >{`${models?.length ?? 0}`}</Text>

          <Refresh
            onClick={async () => {
              const models = await syncModelInfos(typeName);
              if (models.length > 0) {
                setModels(models);
              }
            }}
          />
        </Group>

        <Center
          mr={15}
          style={{
            cursor: "pointer",
          }}
          onClick={(e) => {
            e.stopPropagation();
            openDirModel(true, typeName);
          }}
        >
          <IconFolder
            style={{
              cursor: "pointer",
              height: "20px",
              width: "20px",
              strokeWidth: "1px",
            }}
          />
        </Center>
      </Group>

      <Group align={"start"} p={30} gap={30} flex={1} key={typeName}>
        {models.map((model, index) => {
          return (
            <Stack
              pt={10}
              w={160}
              h={280}
              bg={theme.colors.waLight[1]}
              align={"center"}
              key={model.local_path}
              style={{
                cursor: "pointer",
              }}
              onClick={() => {
                router.push(`/model-detail/?localPath=${model.local_path}`);
              }}
            >
              <ImageLocal
                localPath={model.image_path}
                width={140}
                height={210}
                objectFit={"cover"}
              />
              <Text
                lineClamp={2}
                w={100}
                mb={10}
                style={{
                  fontSize: "10px",
                  fontWeight: "500",
                  wordBreak: "break-all",
                }}
              >{`${displayNameOfModelInfo(model)}`}</Text>
            </Stack>
          );
        })}
      </Group>
    </Stack>
  );
}
