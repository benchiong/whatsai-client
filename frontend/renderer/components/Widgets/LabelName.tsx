import { Text } from "@mantine/core";

export function LabelName({ text }: { text: string }) {
  return (
    <Text
      style={{
        marginLeft: "6px",
        fontSize: "12px",
        fontWeight: 600,
        color: "var(--mantine-color-waDark-7)",
        userSelect: "none",
        minWidth: "80px",
        maxWidth: "160px",
      }}
      lineClamp={1}
    >
      {text}
    </Text>
  );
}
