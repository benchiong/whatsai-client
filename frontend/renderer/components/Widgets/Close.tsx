import { IconX } from "@tabler/icons-react";

export function Close({
  onClick,
  width = 24,
  height = 24,
}: {
  onClick: () => void;
  width?: number;
  height?: number;
}) {
  return (
    <IconX
      style={{
        color: "var(--mantine-color-waLight-9)",
        cursor: "pointer",
        height: `${height}px`,
        width: `${width}px`,
        strokeWidth: "1px",
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
    />
  );
}
