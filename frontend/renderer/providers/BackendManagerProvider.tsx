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
import {
  debug_backend,
  debug_backend_server_url,
  debug_manager,
  debug_manager_url,
} from "../../main/debug";

export type BackendManagerContextType = {
  isManagerReady: boolean;
  isBackendReady: boolean | null; // null for unknown
  managerUrl: string | null;
  backendUrl: string | null;
};

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

export function BackendManagerContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [managerUrl, setManagerUrl] = useState<string | null>(null);
  const [backendUrl, setBackendUrl] = useState<string | null>(null);

  const [isManagerReady, setIsManagerReady] = useState(false);
  const [isBackendReady, setIsBackendReady] = useState<boolean | null>(null);

  // We need it because when backend is ready, it can be not running to response.
  const [isBackendRunning, setIsBackendRunning] = useState<boolean>(false);

  // The install progress after people click the installation button.
  const [progress, setProgress] = useState<ProgressType | null>(null);

  /*  There are 3 Intervals(loops) here:
      1.loop to get managerUrl, then app can communicate with it to get backend server status, how we get
        the url is through IPC, keep looping to ask if app started backend-manager exe file;
      2.After managerUrl set, which means the manager is ready, then we loop to ask if the backend is ready,
        backend's readiness has two steps:
          a. python env/requirements/backend source codes are ready, then people has no necessary to install;
          b. backend server started to response, the state is hold by isBackendRunning
        the two already, we go over from here;
      3.When people's python env(venv/requirements/codes) is not ready, he/she will get an install button,
        installProgressInfoInterval starts then.
   */

  // loop to wait backend manager to be ready through ipc of electron, it's very beginning
  const managerUrlInterval = useInterval(() => {
    window.ipc.send(backendManager, eventBackendManagerUrl);
  }, 1000);

  // loop to require if backend server is ready, **not** the manager server.
  const isBackendReadyInterval = useInterval(() => {
    if (!managerUrl) {
      console.log("empty managerBackendUrl");
      return;
    }
    requestIfBackendReady();
  }, 1000);

  // loop to require what progress of the installation is, start after people click start install button.
  const installProgressInfoInterval = useInterval(() => {
    if (!managerUrl) {
      console.log("empty managerBackendUrl");
      return;
    }
    requestProgressInfo();
  }, 1000);

  useEffect(() => {
    if (debug_backend) {
      return;
    }

    managerUrlInterval.start();

    window.ipc.on(backendManager, (managerUrl) => {
      if (managerUrl) {
        setManagerUrl(managerUrl.toString());
        setIsManagerReady(true);
        managerUrlInterval.stop();
        console.log("backendManager started.");

        isBackendReadyInterval.start();
      }
    });
  }, []);

  // make sure backend is ready.
  const requestIfBackendReady = useCallback(() => {
    console.log("requestIfBackendReady managerBackendUrl:", managerUrl);
    if (!managerUrl) {
      return;
    }
    fetch(`${managerUrl}is_backend_ready`, {
      method: "GET",
    })
      .then((response) => {
        response.json().then((resp) => {
          const { ready, port, backend_running } = resp;
          console.log(ready, port, backend_running);
          if (port) {
            const backendUrl = `http://127.0.0.1:${port}/`;
            setBackendUrl(backendUrl);
          }
          setIsBackendReady(ready);
          setIsBackendRunning(backend_running);
          isBackendReadyInterval.stop();
        });
      })
      .catch((e) => {
        console.log("get backend port error:", e);
      });
  }, [managerUrl]);

  const requestProgressInfo = useCallback(() => {
    fetch(`${managerUrl}install_progress_info`, {
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
            return;
          }

          const p = progress_parsed_result.data;
          setProgress(p);

          if (p.stage == "ready") {
            installProgressInfoInterval.stop();
            isBackendReadyInterval.start();
          } else if (p.stage == "failed") {
            installProgressInfoInterval.stop();
          }
        });
      })
      .catch((e) => {
        console.log("requestInstallProgressInfo error:", e);
        installProgressInfoInterval.stop();
      });
  }, [managerUrl]);

  // install python/requirements/source codes.
  const install_everything = useCallback(() => {
    if (!managerUrl) {
      return;
    }
    fetch(`${managerUrl}install_everything`, {
      method: "GET",
    })
      .then((r) => {})
      .catch((e) => {
        console.log("get backend port error:", e);
      });
  }, [managerUrl]);

  const _manageUrl = debug_manager ? debug_manager_url : managerUrl;
  const _isManagerReady = debug_manager ? true : isManagerReady;
  const _backendUrl = debug_backend ? debug_backend_server_url : backendUrl;
  const _isBackendReady = debug_backend ? true : isBackendReady;

  return (
    <BackendManagerContext.Provider
      value={{
        managerUrl: _manageUrl,
        backendUrl: _backendUrl,
        isManagerReady: _isManagerReady,
        isBackendReady: _isBackendReady,
      }}
    >
      {children}
      {!debug_backend && !isBackendRunning && (
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
                onInstallButtonClick={() => {
                  installProgressInfoInterval.start();
                  if (isBackendReadyInterval.active) {
                    isBackendReadyInterval.stop();
                  }
                }}
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
  onInstallButtonClick,
}: {
  progress: ProgressType | null;
  setProgress: (p: ProgressType) => void;
  install_everything: () => void;
  onInstallButtonClick: () => void;
}) {
  const theme = useMantineTheme();

  if (!progress) {
    return (
      <Button
        w={200}
        h={50}
        onClick={(e) => {
          e.stopPropagation();
          install_everything();
          setProgress({
            stage: "Installing python backend...",
            info: "",
          });
          onInstallButtonClick();
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
