import { Title, useMantineTheme } from "@mantine/core";

export function LabelSingleLine({ text }: { text: string }) {
  const theme = useMantineTheme();

  return (
    <Title
      order={5}
      mt={10}
      h={20}
      c={theme.colors.waDark[9]}
      mx={15}
      style={{
        textAlign: "start",
        userSelect: "none",
        lineHeight: "20px",
        fontSize: "14px",
        fontWeight: "400",
      }}
    >
      {text}
    </Title>
  );
}
