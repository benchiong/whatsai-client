import React, { createContext, useContext, useEffect, useState } from "react";
import { ModelComboDrawer } from "../components/Model/ModelComboDrawer";
import { listModels, syncModelInfos } from "../lib/api";
import {
  ModelInfoArrayType,
  ModelInfoListType,
  ModelInfoType,
} from "../data-type/model";

export type ModelSelectionDrawerContextType = {
  drawerOpened: boolean;
  setDrawerOpened: (opened: boolean) => void;
  toggleDrawer: (
    modelType: string,
    loadFunction: string,
    paramName: string,
    onChange: (model: ModelInfoType) => void,
  ) => void;
  setCardContext: (
    modelType: string,
    loadFunction: string,
    paramName: string,
    onChange: (model: ModelInfoType) => void,
  ) => void;
  displayName: string;
};

const ModelSelectionDrawerContext =
  createContext<ModelSelectionDrawerContextType | null>(null);

export const useModelSelectionDrawerContext = () => {
  const context = useContext(ModelSelectionDrawerContext);
  if (!context) {
    throw new Error(
      "Missing ModelSelectionDrawerContext.Provider in the tree.",
    );
  }
  return context;
};

export function ModelSelectionDrawerProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [drawerOpened, setDrawerOpened] = useState<boolean>(false);
  const [paramName, setParamName] = useState<string>("");
  const [modelType, setModelType] = useState<string>("");
  const [modelLoadFunction, setModelLoadFunction] = useState<string>("");

  // https://stackoverflow.com/questions/55621212/is-it-possible-to-react-usestate-in-react
  const [onChange, setOnChange] = useState<(model: ModelInfoType) => void>(
    () => (model: ModelInfoType) => {},
  );
  const [models, setModels] = useState<ModelInfoListType>([]);

  const setCardContext = (
    modelType: string,
    loadFunction: string,
    paramName: string,
  ) => {
    setModelType(modelType);
    setModelLoadFunction(loadFunction);
    setParamName(paramName);
  };

  const loadModels = (modelLoadFunction: string) => {
    if (!modelLoadFunction) {
      return;
    }
    listModels(modelLoadFunction)
      .then((result) => {
        setModels(result);
      })
      .catch((e) => {
        console.error("loadModels error: " + e);
      });
  };

  const toggleDrawer = (
    mType: string,
    funName: string,
    paramName: string,
    onChange: (model: ModelInfoType) => void,
  ) => {
    if (modelType == mType && drawerOpened) {
      setCardContext("", "", "");
      setOnChange(() => () => {});
      setDrawerOpened(false);
    } else {
      setCardContext(mType, funName, paramName);
      setOnChange(() => (model: ModelInfoType) => onChange(model));
      setDrawerOpened(true);
    }
  };

  useEffect(() => {
    loadModels(modelLoadFunction);
  }, [modelLoadFunction]);

  return (
    <ModelSelectionDrawerContext.Provider
      value={{
        drawerOpened: drawerOpened,
        setDrawerOpened,
        setCardContext: setCardContext,
        toggleDrawer: toggleDrawer,
        displayName: modelType,
      }}
    >
      {children}
      <ModelComboDrawer
        drawerOpened={drawerOpened}
        closeDrawer={() => setDrawerOpened(false)}
        modelType={modelType}
        onModelSelected={(model) => {
          onChange && onChange(model);
        }}
        models={models}
        refreshModels={async () => {
          const models = await syncModelInfos(modelType);
          if (models.length > 0) {
            setModels(models);
          }
        }}
      />
    </ModelSelectionDrawerContext.Provider>
  );
}
