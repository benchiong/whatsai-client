import { IconRefresh } from "@tabler/icons-react";
import { Center, Loader, Tooltip, useMantineTheme } from "@mantine/core";
import { useState } from "react";

export function Refresh({
  asyncOperation,
  width = 24,
  height = 24,
  text = "Refresh models",
}: {
  width?: number;
  height?: number;
  asyncOperation: () => Promise<void>;
  text?: string;
}) {
  const theme = useMantineTheme();
  const [refreshing, setRefreshing] = useState(false);
  return (
    <Tooltip
      label={text}
      zIndex={500}
      radius={5}
      bg={theme.colors.waLight[6]}
      color={theme.colors.waLight[9]}
      style={{
        fontSize: "12px",
      }}
    >
      <Center w={width} h={height}>
        {!refreshing ? (
          <IconRefresh
            style={{
              color: "var(--mantine-color-primary-3)",
              cursor: "pointer",
              height: `${height - 6}px`,
              width: `${width - 6}px`,
              strokeWidth: "1px",
            }}
            onClick={(e) => {
              e.stopPropagation();
              setRefreshing(true);
              asyncOperation()
                .then(() => {
                  setRefreshing(false);
                })
                .catch((e) => {
                  setRefreshing(false);
                });
            }}
          />
        ) : (
          <Loader color={theme.colors.primary[0]} size={"12px"} />
        )}
      </Center>
    </Tooltip>
  );
}
