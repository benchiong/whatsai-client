import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { ModelDownloadingInfoArrayType } from "../data-type/model";
import { getDownloadingInfos } from "../lib/api";
import { useInterval } from "@mantine/hooks";

export type ModelDownloadingContextType = {
  downloadingModels: ModelDownloadingInfoArrayType;
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
  const [downloadingModels, setDownloadingModels] =
    useState<ModelDownloadingInfoArrayType>([]);

  const emptyCountBeforeStop = useRef(5);

  const getDownloadingModels = useCallback(() => {
    getDownloadingInfos()
      .then((downloadInfos) => {
        setDownloadingModels(downloadInfos);
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

  const interval = useInterval(() => getDownloadingModels(), 1000);

  useEffect(() => {
    getDownloadingModels();
  }, []);

  return (
    <ModelDownloadingContext.Provider
      value={{
        downloadingModels,
        startLoop: interval.start,
        stopLoop: interval.stop,
      }}
    >
      {children}
    </ModelDownloadingContext.Provider>
  );
}
