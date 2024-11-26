import { ModelInfoType } from "../../data-type/model";
import {
  Group,
  Center,
  Image,
  Stack,
  Text,
  useMantineTheme,
} from "@mantine/core";
import React from "react";
import {
  civitaiUrl,
  civitSizeStr,
  displayNameOfModelInfo,
} from "../../data-type/helpers";

import Link from "next/link";

export function ModelDetailInfo({ model }: { model: ModelInfoType }) {
  return (
    <Stack p={20}>
      <Stack>
        <ModelInfoTitle
          name={"Model Name"}
          value={displayNameOfModelInfo(model)}
        />
        <BaseInfos model={model} />
        <CivitaiModelInfo model={model} />
      </Stack>
    </Stack>
  );
}

function ModelInfoTitle({ name, value }: { name: string; value: string }) {
  const theme = useMantineTheme();

  return (
    <Group bg={theme.colors.waLight[3]} p={10} my={10}>
      {name && (
        <Text c={theme.colors.waDark[8]} span size={"sm"}>
          {name}:
        </Text>
      )}
      <Text>{value}</Text>
    </Group>
  );
}

function BaseInfos({ model }: { model: ModelInfoType }) {
  return (
    <Stack>
      <ModelInfoTitle name={""} value={"Basic Infos"} />

      {model.model_type && (
        <ParamItem
          key={"Model Type"}
          name={"Model Type"}
          value={model.model_type}
        />
      )}

      {model.file_name && (
        <ParamItem
          key={"File Name"}
          name={"File Name"}
          value={model.file_name}
        />
      )}

      {model.size_kb && (
        <ParamItem
          key={"Model Size"}
          name={"Model Size"}
          value={civitSizeStr(model.size_kb)}
        />
      )}

      {model.local_path && (
        <ParamItem
          key={"Local Path"}
          name={"Local Path"}
          value={model.local_path}
        />
      )}

      {model.sha_256 && (
        <ParamItem key={"SHA 256"} name={"SHA 256"} value={model.sha_256} />
      )}
    </Stack>
  );
}

function CivitaiModelInfo({ model }: { model: ModelInfoType }) {
  const civitModelVersionInfo = model.civit_model;

  if (!civitModelVersionInfo) {
    return (
      <Stack>
        <ModelInfoTitle name={""} value={"CivitAI Model Infos"} />
      </Stack>
    );
  }

  return (
    <Stack>
      <ModelInfoTitle name={""} value={"CivitAI Model Infos"} />
      {civitModelVersionInfo.model?.name && (
        <ParamItem
          key={"Model Name"}
          name={"Model Name"}
          value={civitModelVersionInfo.model?.name}
        />
      )}
      {civitModelVersionInfo.name && (
        <ParamItem
          key={"Version Name"}
          name={"Version Name"}
          value={civitModelVersionInfo.name}
        />
      )}
      {civitModelVersionInfo.baseModel && (
        <ParamItem
          key={"Base Model"}
          name={"Base Model"}
          value={civitModelVersionInfo.baseModel}
        />
      )}
      {civitModelVersionInfo.baseModelType && (
        <ParamItem
          key={"Base Model Type"}
          name={"Base Model Type"}
          value={civitModelVersionInfo.baseModelType}
        />
      )}
      {/*{civitModelVersionInfo.description && (*/}
      {/*  <HtmlItem*/}
      {/*    key={"Description"}*/}
      {/*    name={"Description"}*/}
      {/*    value={civitModelVersionInfo.description}*/}
      {/*  />*/}
      {/*)}*/}

      {civitaiUrl(model) && (
        <UrlItem
          name={"CivitAI Url"}
          key={"civit ulr"}
          value={civitaiUrl(model)!}
        />
      )}
    </Stack>
  );
}

function ParamItem({ name, value }: { name: string; value: any }) {
  const theme = useMantineTheme();
  return (
    <Group>
      <Text
        m={0}
        w={100}
        style={{
          textAlign: "right",
          fontSize: "14px",
        }}
      >
        {name}:
      </Text>
      <Text
        ml={20}
        p={5}
        px={15}
        maw={400}
        bg={theme.colors.waLight[5]}
        style={{
          maxLines: 5,
          fontSize: "12px",
          maxWidth: "400px",
          wordBreak: "break-all",
        }}
      >
        {value}
      </Text>
    </Group>
  );
}

function HtmlItem({ name, value }: { name: string; value: any }) {
  const theme = useMantineTheme();
  return (
    <Group>
      <Text
        w={100}
        style={{
          textAlign: "right",
          fontSize: "14px",
        }}
      >
        {name}:
      </Text>
      <div dangerouslySetInnerHTML={{ __html: value }} />
    </Group>
  );
}

function UrlItem({ name, value }: { name: string; value: string }) {
  return (
    <Group align={"center"}>
      <Center>
        <Text
          w={100}
          style={{
            textAlign: "right",
            fontSize: "14px",
          }}
        >
          {name}:
        </Text>
      </Center>

      <Link href={value} target={"_blank"} onClick={(e) => e.stopPropagation()}>
        <Group gap={5} my={5} ml={20}>
          <Image h={22} src={"/images/civitai-icon.png"} w={16} />
        </Group>
      </Link>
    </Group>
  );
}
