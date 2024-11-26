import {
  Modal,
  Stack,
  Text,
  TextInput,
  Button,
  Table,
  Group,
  Center,
  Tooltip,
  useMantineTheme,
  Radio,
} from "@mantine/core";
import React, { useCallback, useEffect, useState } from "react";
import {
  addModelDir,
  getModelDir,
  isDirOk,
  removeModelDir,
  setDefaultModelDir,
} from "../../lib/api";
import { ModelDirType } from "../../data-type/model";
import { IconCircleMinus } from "@tabler/icons-react";
import { showErrorNotification } from "../../utils/notifications";

export function ModelDirModal({
  opened,
  modelType,
  onClose,
}: {
  opened: boolean;
  modelType: string;
  onClose: () => void;
}) {
  const theme = useMantineTheme();

  const [path, setPath] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorInfo, setErrorInfo] = useState("");
  const [modelDirInfo, setModelDirInfo] = useState<ModelDirType | null>(null);
  const [dirToRemove, setDirToRemove] = useState("");

  const getModelDirInfo = useCallback(() => {
    if (!modelType) {
      return;
    }
    getModelDir(modelType).then((dirInfo) => {
      setModelDirInfo(dirInfo);
    });
  }, [modelType]);

  useEffect(() => {
    getModelDirInfo();
  }, [modelType]);

  const rows = modelDirInfo ? (
    modelDirInfo.dirs.map((dirInfo, index) => (
      <Table.Tr key={dirInfo.dir}>
        <Table.Td>{dirInfo.dir}</Table.Td>
        <Table.Td>{dirInfo.model_count}</Table.Td>
        <Table.Td>
          <Center>
            <Radio
              checked={dirInfo.is_default}
              onChange={(e) => {
                e.stopPropagation();
                setDefaultModelDir(modelType, dirInfo.dir).then((resp) => {
                  if (resp?.record) {
                    setModelDirInfo(resp.record);
                  } else {
                    showErrorNotification({
                      error: Error("Set default dir failed"),
                      reason: resp?.error_info ?? "",
                    });
                  }
                });
              }}
            />
          </Center>
        </Table.Td>
        <Table.Td>
          <Group w={60} justify={"center"}>
            <Tooltip
              label="Remove dir"
              zIndex={500}
              radius={5}
              bg={theme.colors.waLight[6]}
              color={theme.colors.waLight[9]}
              style={{
                fontSize: "12px",
              }}
            >
              <IconCircleMinus
                style={{
                  width: "20px",
                  height: "20px",
                  strokeWidth: "1px",
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  console.log(dirInfo.dir);
                  setDirToRemove(dirInfo.dir);
                }}
              />
            </Tooltip>
          </Group>
        </Table.Td>

        <Table.Td></Table.Td>
      </Table.Tr>
    ))
  ) : (
    <></>
  );

  return (
    <Modal
      opened={opened}
      withCloseButton={true}
      title={`Dirs of ${modelType}`}
      onClose={() => {
        setPath("");
        setLoading(false);
        setDirToRemove("");
        onClose();
      }}
      radius={10}
      transitionProps={{ duration: 100 }}
      size={"xl"}
    >
      <Stack>
        {modelDirInfo && (
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Dir Path</Table.Th>
                <Table.Th>Model Count</Table.Th>
                <Table.Th>Default </Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{rows}</Table.Tbody>
          </Table>
        )}

        <Stack
          p={15}
          px={20}
          my={20}
          bg={theme.colors.waLight[3]}
          w={"100%"}
          h={120}
          align={"center"}
          style={{
            // border: "0.2px solid var(--mantine-color-primary-3)",
            borderRadius: "5px",
          }}
        >
          {!dirToRemove ? (
            <>
              <TextInput
                placeholder={`Local dir path of ${modelType} to add.`}
                flex={1}
                w={"100%"}
                radius={"sm"}
                onChange={(e) => setPath(e.target.value)}
              />
              {errorInfo && (
                <Text
                  style={{
                    fontSize: "12px",
                    color: "red",
                  }}
                >
                  {errorInfo}
                </Text>
              )}
              <Button
                mr={5}
                w={100}
                loading={loading}
                disabled={!path}
                onClick={(e) => {
                  isDirOk(path).then((resp) => {
                    if (resp == "ok") {
                      setErrorInfo("");
                      let trimmedPath = path.trim();
                      addModelDir(modelType, trimmedPath, false).then(
                        (resp) => {
                          if (resp && resp.record) {
                            setModelDirInfo(resp.record);
                          } else {
                            showErrorNotification({
                              error: Error("Add dir failed"),
                              reason: resp?.error_info ?? "",
                            });
                          }
                        },
                      );
                    } else {
                      setErrorInfo(resp);
                    }
                  });
                  e.stopPropagation();
                }}
              >{`Add dir`}</Button>
            </>
          ) : (
            <Stack gap={5} w={"100%"} align={"center"}>
              <Text
                style={{
                  fontSize: "16px",
                }}
              >{`Confirm to remove Dir`}</Text>
              <Text
                style={{
                  fontSize: "12px",
                }}
              >{`${dirToRemove} `}</Text>
              <Group h={40}>
                <Button
                  h={26}
                  onClick={(e) => {
                    e.stopPropagation();
                    removeModelDir(modelType, dirToRemove).then(
                      (modelDirInfoResp) => {
                        if (modelDirInfoResp?.record) {
                          setModelDirInfo(modelDirInfoResp.record);
                          setDirToRemove("");
                        }
                      },
                    );
                  }}
                >
                  Confirm
                </Button>
                <Button
                  h={26}
                  c={theme.colors.waDark[5]}
                  bg={theme.colors.waLight[4]}
                  onClick={(e) => {
                    e.stopPropagation();
                    setDirToRemove("");
                  }}
                >
                  Cancel
                </Button>
              </Group>
            </Stack>
          )}
        </Stack>
      </Stack>
    </Modal>
  );
}
