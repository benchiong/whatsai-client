import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  DownloadingModelTaskArrayType,
  ModelDownloadingInfoArrayType,
} from "../data-type/model";
import { cancelDownloadTask, getDownloadingInfos } from "../lib/api";
import { useInterval } from "@mantine/hooks";

export type ModelDownloadingContextType = {
  downloadingTasks: DownloadingModelTaskArrayType;
  cancelDownloadingTask: (taskId: string) => void;
  startLoop: () => void;
  stopLoop: () => void;
};

export const ModelDownloadingContext =
  createContext<ModelDownloadingContextType | null>(null);

export const useModelDownloadingContext = () => {
  const context = useContext(ModelDownloadingContext);
  if (!context) {
    throw new Error("Missing ModelDownloadingContext.Provider in the tree.");
  }
  return context;
};

export function ModelDownloadingContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [downloadingTasks, setDownloadingTasks] =
    useState<DownloadingModelTaskArrayType>([]);

  const emptyCountBeforeStop = useRef(5);

  const getDownloadingTasks = useCallback(() => {
    getDownloadingInfos()
      .then((downloadInfos) => {
        setDownloadingTasks(downloadInfos);
        if (downloadInfos.length == 0) {
          if (emptyCountBeforeStop.current <= 0) {
            interval.stop();
            emptyCountBeforeStop.current = 5;
          } else {
            emptyCountBeforeStop.current -= 1;
          }
        } else {
          interval.start();
        }
      })
      .catch((e) => console.error("getDownloadingInfos failed:", e));
  }, []);

  const interval = useInterval(() => getDownloadingTasks(), 1000);

  useEffect(() => {
    getDownloadingTasks();
  }, []);

  const cancelDownloadingTask = useCallback((workloadId: string) => {
    if (!workloadId) {
      return;
    }

    cancelDownloadTask(workloadId)
      .then((r) => {})
      .catch((e) => {
        console.error(e);
      });
  }, []);

  return (
    <ModelDownloadingContext.Provider
      value={{
        cancelDownloadingTask,
        downloadingTasks: downloadingTasks,
        startLoop: interval.start,
        stopLoop: interval.stop,
      }}
    >
      {children}
    </ModelDownloadingContext.Provider>
  );
}
