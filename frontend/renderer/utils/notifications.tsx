import { notifications, showNotification } from "@mantine/notifications";
import { IconCheck, IconX, IconInfoCircle } from "@tabler/icons-react";
import React from "react";

export function showErrorNotification({
  error,
  reason,
  title = "Something went wrong, retry may help.",
  autoClose = 3000,
}: {
  error: Error | { message: string } | { message: string }[];
  reason?: string;
  title?: string;
  autoClose?: number | false;
}) {
  const message = Array.isArray(error) ? (
    <ul>
      {error.map((e, index) => (
        <li key={index}>{e.message}</li>
      ))}
    </ul>
  ) : (
    (reason ?? error.message)
  );

  notifications.show({
    icon: <IconX size={18} />,
    color: "red",
    message,
    title,
    autoClose,
  });
}

export function showSuccessNotification({
  message,
  title,
  autoClose = 3000,
}: {
  message: string | React.ReactNode;
  title?: string;
  autoClose?: number | false;
}) {
  showNotification({
    icon: <IconCheck size={18} />,
    color: "teal",
    message,
    title,
    autoClose,
  });
}

export function showNormalNotification({
  message,
  title,
  autoClose = 3000,
}: {
  message: string | React.ReactNode;
  title?: string;
  autoClose?: number | false;
}) {
  showNotification({
    icon: <IconInfoCircle size={18} />,
    color: "orange",
    message,
    title,
    autoClose,
  });
}
