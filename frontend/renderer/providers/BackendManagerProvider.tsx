import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  backendManager,
  eventBackendManagerUrl,
} from "../../main/ipc-constants";
import { useInterval } from "@mantine/hooks";
import {
  Overlay,
  useMantineTheme,
  Center,
  Image,
  Button,
  Stack,
  Progress,
  Text,
  Title,
} from "@mantine/core";
import { z } from "zod";

export type BackendManagerContextType = {
  isBackendManagerReady: boolean;
  isBackendReady: boolean | null; // null for unknown
  managerBackendUrl: string | null;
  backendUrl: string | null;
};

const isProd = process.env.NODE_ENV === "production";

export const BackendManagerContext =
  createContext<BackendManagerContextType | null>(null);

export const useBackendManagerContext = () => {
  const context = useContext(BackendManagerContext);
  if (!context) {
    throw new Error("Missing BackendManagerContext.Provider in the tree.");
  }
  return context;
};

const ProgressTypeSchema = z.object({
  stage: z.string().nullable().optional(),
  info: z.string().nullable().optional(),
  progress: z
    .object({
      percent: z.number().optional().nullable(),
      downloaded_size: z.number().optional().nullable(),
      total_size: z.number().optional().nullable(),
    })
    .optional()
    .nullable(),
});

type ProgressType = z.infer<typeof ProgressTypeSchema>;

interface UseIntervalReturnType {
  start: () => void;
  stop: () => void;
  toggle: () => void;
  active: boolean;
}

// todo: rubbish here, refactor
export function BackendManagerContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const theme = useMantineTheme();
  const [managerBackendUrl, setManagerBackendUrl] = useState<string | null>(
    null,
  );
  const [backendUrl, setBackendUrl] = useState<string | null>(null);

  // leave them, used for instance state, urls are used initial state.
  const [isBackendManagerReady, setIsBackendManagerReady] = useState(false);
  const [isBackendReady, setIsBackendReady] = useState<boolean | null>(null);
  const [isBackendRunning, setIsBackendRunning] = useState<boolean>(false);

  const [progress, setProgress] = useState<ProgressType | null>(null);

  // loop to wait backend manager to be ready through ipc of electron, it's very beginning
  const interval = useInterval(() => {
    window.ipc.send(backendManager, eventBackendManagerUrl);
  }, 1000);

  const requestInstallProgressInfo = () => {
    if (!managerBackendUrl) {
      console.log("empty managerBackendUrl");
      return;
    }
    console.log("requestInstallProgressInfo");
    fetch(`${managerBackendUrl}install_progress_info`, {
      method: "GET",
    })
      .then((response) => {
        response.json().then((resp) => {
          const progress_parsed_result = ProgressTypeSchema.safeParse(resp);
          if (!progress_parsed_result.success) {
            console.log(
              "Parse progress response error:",
              progress_parsed_result.error.issues,
            );
            installProgressInfoInterval.stop();
            return;
          }
          const p = progress_parsed_result.data;
          console.log("Progress:", p);
          setProgress(p);
          if (p.stage == "ready") {
            installProgressInfoInterval.stop();
            backendReady();
          } else if (p.stage == "failed") {
            installProgressInfoInterval.stop();
            backendReady();
          }
        });
      })
      .catch((e) => {
        console.log("requestInstallProgressInfo error:", e);
        installProgressInfoInterval.stop();
      });
  };

  // loop to listen what progress of the installation
  const installProgressInfoInterval = useInterval(() => {
    requestInstallProgressInfo();
  }, 1000);

  useEffect(() => {
    window.ipc.on(backendManager, (managerUrl) => {
      if (managerUrl) {
        setManagerBackendUrl(managerUrl.toString());
        setIsBackendManagerReady(true);
        interval.stop();
      }
    });
  }, []);

  useEffect(() => {
    if (!isProd) {
      setIsBackendReady(true);
      setIsBackendRunning(true);
      return;
    }
    if (!managerBackendUrl) {
      return;
    }
    backendReady();
  }, [managerBackendUrl]);

  // make sure backend is ready.
  const backendReady = () => {
    if (!managerBackendUrl) {
      return;
    }
    fetch(`${managerBackendUrl}is_backend_ready`, {
      method: "GET",
    })
      .then((response) => {
        response.json().then((resp) => {
          const { ready, port, backend_running } = resp;
          if (port) {
            const backendUrl = `http://127.0.0.1:${port}/`;
            setBackendUrl(backendUrl);
          }
          setIsBackendReady(ready);
          setIsBackendRunning(backend_running);
        });
      })
      .catch((e) => {
        console.log("get backend port error:", e);
      });
  };

  const install_everything = useCallback(() => {
    if (!managerBackendUrl) {
      return;
    }
    fetch(`${managerBackendUrl}install_everything`, {
      method: "GET",
    })
      .then((r) => {})
      .catch((e) => {
        console.log("get backend port error:", e);
      });
  }, [managerBackendUrl]);

  useEffect(() => {
    interval.start();
  }, [managerBackendUrl]);

  return (
    <BackendManagerContext.Provider
      value={{
        managerBackendUrl,
        backendUrl,
        isBackendManagerReady,
        isBackendReady,
      }}
    >
      {children}
      {!isBackendRunning && (
        <Overlay
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "var(--mantine-color-waLight-0)",
            zIndex: 9999,
          }}
        >
          <Center h={"100%"} w={"100%"}>
            {isBackendReady == false ? (
              <InstallButtonOrProgressInfo
                progress={progress}
                setProgress={setProgress}
                install_everything={install_everything}
                installProgressInfoInterval={installProgressInfoInterval}
              />
            ) : (
              <Image src={"/images/logo.png"} w={100} h={100} />
            )}
          </Center>
        </Overlay>
      )}
    </BackendManagerContext.Provider>
  );
}

function InstallButtonOrProgressInfo({
  progress,
  install_everything,
  setProgress,
  installProgressInfoInterval,
}: {
  progress: ProgressType | null;
  setProgress: (p: ProgressType) => void;
  install_everything: () => void;
  installProgressInfoInterval: UseIntervalReturnType;
}) {
  const theme = useMantineTheme();

  console.log(progress);

  if (!progress) {
    return (
      <Button
        w={200}
        h={50}
        onClick={(e) => {
          e.stopPropagation();
          install_everything();
          installProgressInfoInterval.start();
          setProgress({
            stage: "Installing python backend...",
            info: "",
          });
        }}
      >
        Install python backend
      </Button>
    );
  }

  return (
    <Stack
      w={400}
      h={200}
      bg={theme.colors.waLight[2]}
      style={{
        borderRadius: "5px",
      }}
      align={"center"}
      py={10}
    >
      <Title order={4}>Backend installing</Title>
      <Text
        bg={theme.colors.waLight[5]}
        p={5}
        px={10}
        style={{
          fontSize: "14px",
          fontWeight: 500,
          color: "var(--mantine-color-waDark-6)",
          userSelect: "none",
          textAlign: "center",
          borderRadius: "3px",
        }}
      >
        {`${progress.stage}`}
      </Text>
      {progress.info && (
        <Text
          bg={theme.colors.waLight[5]}
          p={5}
          px={10}
          style={{
            fontSize: "14px",
            fontWeight: 500,
            color: "var(--mantine-color-waDark-6)",
            userSelect: "none",
            textAlign: "center",
            borderRadius: "3px",
            wordBreak: "break-all",
          }}
        >
          {progress.info}
        </Text>
      )}

      {progress.progress?.percent && (
        <Progress
          w={"100%"}
          radius={"none"}
          color={"green.4"}
          mb={-4}
          h={4}
          style={{
            zIndex: 601,
          }}
          value={progress.progress.percent * 100}
        />
      )}
    </Stack>
  );
}
