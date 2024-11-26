import React, { createContext, useContext } from "react";
import { useLocalStorage } from "@mantine/hooks";
import superjson from "superjson";
import { generateRandomString } from "ts-randomstring/lib";

export type ClientIdContextType = {
  clientId: string;
};

export const ClientIdContext = createContext<ClientIdContextType | null>(null);

export const useClientIdContext = () => {
  const context = useContext(ClientIdContext);
  if (!context) {
    throw new Error("Missing ClientIdContext.Provider in the tree.");
  }
  return context;
};

export function ClientIdContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [value] = useLocalStorage({
    key: "WhatsAI-ClientId",
    defaultValue: generateRandomString({ length: 24 }),
    serialize: superjson.stringify,
    deserialize: (str) => {
      if (str) {
        return superjson.parse(str);
      }
      return generateRandomString({ length: 24 });
    },
  });

  return (
    <ClientIdContext.Provider value={{ clientId: value }}>
      {children}
    </ClientIdContext.Provider>
  );
}
