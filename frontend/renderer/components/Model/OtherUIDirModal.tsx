import {
  Button,
  Group,
  Modal,
  Stack,
  Table,
  Input,
  InputBase,
  TextInput,
  Text,
  Combobox,
  useCombobox,
  useMantineTheme,
} from "@mantine/core";
import React, { useCallback, useEffect, useState } from "react";
import { addOtherUIDirs, getOtherUIPathMap } from "../../lib/api";
import { UIMapType } from "../helpers";

export function OtherUIDirModal({
  opened,
  onClose,
}: {
  opened: boolean;
  onClose: () => void;
}) {
  const theme = useMantineTheme();
  const [UIName, setUIName] = useState("WebUI");
  const [dir, setDir] = useState("");
  const [UIMap, setUIMap] = useState<UIMapType>({});
  const [addedDirs, setAddedDirs] = useState<string[][]>([]);

  const dirWithSlash = dir.endsWith("/") ? dir : dir + "/";
  const UINames = ["WebUI", "ComfyUI"];

  const baseDirTip =
    UIName === "WebUI" ? ".../stable-diffusion-webui/" : ".../ComfyUI/";

  useEffect(() => {
    if (!dir) {
      setUIMap({});
    }
    getOtherUIPathMap(UIName).then((r) => {
      setUIMap(r);
    });
  }, [UIName, dir]);

  const combobox = useCombobox({
    onDropdownClose: () => combobox.resetSelectedOption(),
  });

  const calRows = useCallback(
    (UIMap: UIMapType) => {
      if (!dir) {
        return;
      }
      let keys = Object.keys(UIMap);
      const results = [];
      for (let i = 0; i < keys.length; i++) {
        const key = keys[i];
        let value = UIMap[key];

        if (value instanceof Array) {
          value = value.join(",\n");
        }

        results.push(
          <Table.Tr key={key}>
            <Table.Td>{key}</Table.Td>
            <Table.Td>{`${dirWithSlash}${value}`}</Table.Td>
          </Table.Tr>,
        );
      }
      return results;
    },
    [dir],
  );

  return (
    <Modal
      opened={opened}
      withCloseButton={true}
      title={`Add WebUI/ComfyUI models.`}
      onClose={() => {
        setUIMap({});
        setDir("");
        setAddedDirs([]);
        onClose();
      }}
      radius={10}
      transitionProps={{ duration: 100 }}
      size={"lg"}
      zIndex={500}
    >
      <Stack align={"center"}>
        <Group
          p={15}
          px={20}
          bg={theme.colors.waLight[0]}
          w={"100%"}
          style={{
            borderRadius: "5px",
            position: "sticky",
            top: "0px",
            zIndex: 300,
          }}
        >
          <Combobox
            store={combobox}
            onOptionSubmit={(val) => {
              setUIName(val);
              combobox.closeDropdown();
            }}
            zIndex={510}
            radius={10}
            // w={120}
          >
            <Combobox.Target>
              <InputBase
                component="button"
                type="button"
                pointer
                rightSection={<Combobox.Chevron />}
                rightSectionPointerEvents="none"
                onClick={() => combobox.toggleDropdown()}
              >
                {UIName || <Input.Placeholder>Pick value</Input.Placeholder>}
              </InputBase>
            </Combobox.Target>

            <Combobox.Dropdown>
              <Combobox.Options>
                {UINames.map((item) => (
                  <Combobox.Option value={item} key={item}>
                    {item}
                  </Combobox.Option>
                ))}
              </Combobox.Options>
            </Combobox.Dropdown>
          </Combobox>

          <TextInput
            placeholder={`${UIName} base dir here, e.g. ${baseDirTip}`}
            flex={1}
            radius={"sm"}
            onChange={(e) => setDir(e.target.value)}
          />
        </Group>
        {addedDirs.length > 0 && <Text>Added Dirs</Text>}

        {addedDirs.length == 0 && dir && UIMap && (
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Model Type</Table.Th>
                <Table.Th>Path</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{calRows(UIMap)}</Table.Tbody>
          </Table>
        )}

        {addedDirs.length > 0 && (
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Model Type</Table.Th>
                <Table.Th>Path</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {addedDirs.map((item) => {
                const modelType = item[0];
                const dir = item[1];
                return (
                  <Table.Tr key={modelType}>
                    <Table.Td>{modelType}</Table.Td>
                    <Table.Td>{dir}</Table.Td>
                  </Table.Tr>
                );
              })}
            </Table.Tbody>
          </Table>
        )}

        <Button
          w={140}
          mr={5}
          my={10}
          disabled={!dir || addedDirs.length > 0}
          onClick={() => {
            addOtherUIDirs(UIName, dir).then((resp) => {
              const addedDirs = resp?.added_paths;
              if (addedDirs) {
                setAddedDirs(addedDirs);
              } else {
                setAddedDirs([]);
              }
            });
          }}
        >{`Add dirs`}</Button>
      </Stack>
    </Modal>
  );
}
