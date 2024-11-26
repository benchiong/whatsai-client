import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

import { AppProps } from "next/app";
import React, { ReactElement, ReactNode, useMemo } from "react";
import { NextPage } from "next";
import { AppLayout } from "../components/AppLayout/AppLayout";
import {
  createTheme,
  MantineProvider,
  virtualColor,
  colorsTuple,
} from "@mantine/core";
import { Notifications } from "@mantine/notifications";

import { RecoilRoot, RecoilEnv } from "recoil";
import { TasksContextProvider } from "../providers/TasksProvider";
import { ClientIdContextProvider } from "../providers/ClientIdProvider";

// https://github.com/facebookexperimental/Recoil/issues/733#issuecomment-1399410023
RecoilEnv.RECOIL_DUPLICATE_ATOM_KEY_CHECKING_ENABLED = false;

type CustomNextPage = NextPage & {
  getLayout?: (page: ReactElement) => ReactNode;
};

type CustomAppProps = {
  Component: CustomNextPage;
} & AppProps;

const mantineTheme = createTheme({
  fontFamily: "Montserrat, sans-serif",
  defaultRadius: "xl",
  focusRing: "never",
  breakpoints: {
    xs: "30em",
    sm: "48em",
    md: "64em",
    lg: "74em",
    xl: "90em",
  },
  white: "#fefefe",
  black: "#222222",
  cursorType: "pointer", // https://mantine.dev/core/switch/

  primaryColor: "accent",
  colors: {
    customBlue: virtualColor({
      name: "customBlue",
      dark: "darkCustomBlue",
      light: "lightCustomBlue",
    }),
    darkCustomBlue: colorsTuple("#003759"),
    lightCustomBlue: colorsTuple("#A1E3F7"),

    customPurple: virtualColor({
      name: "customPurple",
      dark: "darkCustomPurple",
      light: "lightCustomPurple",
    }),
    darkCustomPurple: colorsTuple("#3C1C3C"),
    lightCustomPurple: colorsTuple("#DAB1DA"),

    customYellow: virtualColor({
      name: "customYellow",
      dark: "darkCustomYellow",
      light: "lightCustomYellow",
    }),
    darkCustomYellow: colorsTuple("#646400"),
    lightCustomYellow: colorsTuple("#DFD920"),
    customGreen: virtualColor({
      name: "customGreen",
      dark: "darkCustomGreen",
      light: "lightCustomGreen",
    }),
    darkCustomGreen: colorsTuple("#0E440E"),
    lightCustomGreen: colorsTuple("#88E788"),

    customPink: virtualColor({
      name: "customPink",
      dark: "darkCustomPink",
      light: "lightCustomPink",
    }),
    darkCustomPink: colorsTuple("#330F14"),
    lightCustomPink: colorsTuple("#FFB5C0"),

    waDark: virtualColor({
      name: "waDark",
      dark: "waDarkComplementary",
      light: "waDarkPrimary",
    }),
    waLight: virtualColor({
      name: "waLight",
      dark: "waLightComplementary",
      light: "waLightPrimary",
    }),
    primary: virtualColor({
      name: "primary",
      dark: "accentComplementary",
      light: "accent",
    }),
    phOrange: colorsTuple("#ff9000"), // a sexy color, be sexy is cool, but be dirty is not :(
    accent: [
      "#fff5e1",
      "#ffeacc",
      "#ffd49b",
      "#ffbc64",
      "#ffa738",
      "#ff9a1b",
      "#ff9409",
      "#e38000",
      "#ca7100",
      "#b06000",
    ],
    accentComplementary: [
      "#b06000",
      "#ca7100",
      "#e38000",
      "#ff9409",
      "#ff9a1b",
      "#ffa738",
      "#ffbc64",
      "#ffd49b",
      "#ffeacc",
      "#fff5e1",
    ],
    waLightPrimary: [
      "#fefefe",
      "#fafafa",
      "#f6f6f6",
      "#f0f0f0",
      "#eaeaea",
      "#e1e1e1",
      "#d2d2d2",
      "#c1c1c1",
      "#b2b2b2",
      "#a1a1a1",
      "#929292",
    ],
    waLightComplementary: [
      "#222222",
      "#292929",
      "#313131",
      "#373737",
      "#404040",
      "#4f4f4f",
      "#606060",
      "#6f6f6f",
      "#808080",
      "#8f8f8f",
      "#929292",
    ],
    waDarkPrimary: [
      "#222222",
      "#292929",
      "#2f2f2f",
      "#382828",
      "#3e2e2e",
      "#4f4f4f",
      "#5e5e5e",
      "#6f6f6f",
      "#7e7e7e",
      "#8f8f8f",
    ],
    waDarkComplementary: [
      "#ffffff",
      "#f8f8f8",
      "#f2f2f2",
      "#e9f9f9",
      "#e3f3f3",
      "#d2d2d2",
      "#c3c3c3",
      "#b2b2b2",
      "#a3a3a3",
      "#929292",
    ],
  },
});

function MyApp({ Component, pageProps }: CustomAppProps) {
  const getLayout = useMemo(() => {
    return (
      Component.getLayout ??
      ((page: React.ReactElement) => <AppLayout>{page}</AppLayout>)
    );
  }, [Component.getLayout]);

  return (
    <RecoilRoot>
      <MantineProvider theme={mantineTheme} defaultColorScheme={"dark"}>
        <ClientIdContextProvider>
          <TasksContextProvider>
            <Notifications />
            {getLayout(<Component {...pageProps} />)}
          </TasksContextProvider>
        </ClientIdContextProvider>
      </MantineProvider>
    </RecoilRoot>
  );
}

export default MyApp;
