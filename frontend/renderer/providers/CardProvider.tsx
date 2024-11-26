import React, { createContext, useContext, useState } from "react";

export type CardContextType = {
  cardName: string;
  setCardName: (cardName: string) => void;
  onGenerate: () => void;
  registerOnGenerateCallback: (cb: () => void, key: string) => void;
};

export const CardContext = createContext<CardContextType | null>(null);

export const useCardContext = () => {
  const context = useContext(CardContext);
  if (!context) {
    throw new Error("Missing CardContext.Provider in the tree.");
  }
  return context;
};

export type CallBackType = {
  [key: string]: () => void;
};
export function CardContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  let cbs: CallBackType = {};
  const [cardName, setCardName] = useState("");

  return (
    <CardContext.Provider
      value={{
        cardName,
        setCardName,
        onGenerate: () => {
          for (const key in cbs) {
            cbs[key]();
          }
        },
        registerOnGenerateCallback: (cb, key) => {
          cbs[key] = cb;
        },
      }}
    >
      {children}
    </CardContext.Provider>
  );
}
