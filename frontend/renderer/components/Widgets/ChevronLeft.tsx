import { IconCircleChevronLeft } from "@tabler/icons-react";
import { useMantineTheme } from "@mantine/core";

export function ChevronLeft({
  onClick,
  disabled = false,
}: {
  onClick: () => void;
  disabled?: boolean;
}) {
  const theme = useMantineTheme();

  return (
    <IconCircleChevronLeft
      color={disabled ? theme.colors.waDark[9] : theme.colors.primary[3]}
      style={{
        cursor: "pointer",
        height: "22px",
        width: "22px",
        strokeWidth: "1px",
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
    />
  );
}
