import React from "react";
import {
  Center,
  Stack,
  Tooltip,
  useMantineColorScheme,
  useMantineTheme,
} from "@mantine/core";
import {
  IconFile3d,
  IconPhotoAi,
  IconPlayCard5,
  IconBrightnessFilled,
  IconTestPipe,
  IconProps,
  Icon,
} from "@tabler/icons-react";
import Link from "next/link";
import { useRouter } from "next/router";
import { NAV_WIDTH } from "../../extras/constants";
import * as react from "react";

interface IconMap {
  [key: string]: react.ForwardRefExoticComponent<
    IconProps & react.RefAttributes<Icon>
  >;
}

const ICON_MAP: IconMap = {
  IconFile3d,
  IconPhotoAi,
  IconPlayCard5,
  IconBrightnessFilled,
  IconTestPipe,
};

const isProd = process.env.NODE_ENV === "production";

export function AppHeader() {
  const theme = useMantineTheme();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();

  return (
    <Stack
      w={NAV_WIDTH}
      bg={theme.colors.waLight[4]}
      justify={"space-between"}
      h={"100hv"}
    >
      <Stack h={500} align={"center"} gap={40} mt={40}>
        <NavItem href={"/home/"} icon={"IconPlayCard5"} text={"Cards"} />
        <NavItem href={"/models/"} icon={"IconFile3d"} text={"Models"} />
        <NavItem href={"/artworks/"} icon={"IconPhotoAi"} text={"Artworks"} />
        {!isProd && (
          <NavItem
            href={"/playground/"}
            icon={"IconTestPipe"}
            text={"Playground"}
          />
        )}
      </Stack>
      <Stack h={300} align={"center"} justify={"end"} mb={10}>
        <Tooltip
          label={"Dark/Light"}
          position={"right"}
          onClick={() => toggleColorScheme()}
        >
          <IconBrightnessFilled
            style={{
              cursor: "pointer",
            }}
          />
        </Tooltip>
        <Tooltip
          label={"Alpha Version"}
          position={"right"}
          onClick={() => toggleColorScheme()}
        >
          <Center w={40} mb={10}>
            <Alpha />
          </Center>
        </Tooltip>
      </Stack>
    </Stack>
  );
}

function NavItem({
  href,
  icon,
  text,
}: {
  href: string;
  icon: string;
  text: string;
}) {
  const theme = useMantineTheme();
  const Icon = ICON_MAP[icon];
  const router = useRouter();

  const selected = router.asPath == href;

  const bg = selected ? "var(--mantine-color-primary-3)" : "none";

  return (
    <Link href={href}>
      <Tooltip
        label={text}
        zIndex={500}
        radius={5}
        bg={theme.colors.waLight[6]}
        color={theme.colors.waLight[9]}
        style={{
          fontSize: "12px",
        }}
        position={"right"}
      >
        <Center
          style={{
            width: "36px",
            height: "36px",
            background: bg,
            borderRadius: "20px",
          }}
        >
          <Icon
            color={selected ? theme.white : theme.colors.phOrange[1]}
            style={{
              width: "30px",
              strokeWidth: "1px",
            }}
          />
        </Center>
      </Tooltip>
    </Link>
  );
}

export function Beta() {
  return (
    <svg viewBox="0 0 28 11" version="1.1" xmlns="http://www.w3.org/2000/svg">
      <g stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
        <g>
          <rect
            fill="#2DB35A"
            x="0"
            y="0"
            width="28"
            height="11"
            rx="5.5"
          ></rect>
          <g
            id="Beta"
            transform="translate(5.765, 1.7)"
            fill="#FFFFFF"
            fillRule="nonzero"
          >
            <path d="M3.33,4.878 C3.33,5.394 3.2115,5.76 2.9745,5.976 C2.7375,6.192 2.346,6.3 1.8,6.3 L0,6.3 L0,0 L1.692,0 C2.226,0 2.6175,0.108 2.8665,0.324 C3.1155,0.54 3.24,0.9 3.24,1.404 L3.24,1.917 C3.24,2.379 3.075,2.727 2.745,2.961 C3.135,3.177 3.33,3.546 3.33,4.068 L3.33,4.878 Z M2.457,1.323 C2.457,1.095 2.4045,0.93 2.2995,0.828 C2.1945,0.726 2.028,0.675 1.8,0.675 L0.783,0.675 L0.783,2.664 L1.8,2.664 C1.986,2.664 2.142,2.604 2.268,2.484 C2.394,2.364 2.457,2.205 2.457,2.007 L2.457,1.323 Z M2.547,3.987 C2.547,3.789 2.487,3.6315 2.367,3.5145 C2.247,3.3975 2.088,3.339 1.89,3.339 L0.783,3.339 L0.783,5.625 L1.881,5.625 C2.109,5.625 2.277,5.5725 2.385,5.4675 C2.493,5.3625 2.547,5.196 2.547,4.968 L2.547,3.987 Z"></path>
            <path d="M6.471,6.3 C5.943,6.3 5.556,6.1875 5.31,5.9625 C5.064,5.7375 4.941,5.37 4.941,4.86 L4.941,3.24 C4.941,2.724 5.052,2.355 5.274,2.133 C5.496,1.911 5.865,1.8 6.381,1.8 L6.804,1.8 C7.23,1.8 7.5525,1.9185 7.7715,2.1555 C7.9905,2.3925 8.1,2.739 8.1,3.195 L8.1,4.365 L5.706,4.365 L5.706,5.04 C5.706,5.226 5.763,5.37 5.877,5.472 C5.991,5.574 6.159,5.625 6.381,5.625 L7.812,5.625 L7.812,6.3 L6.471,6.3 Z M7.353,3.015 C7.353,2.859 7.302,2.73 7.2,2.628 C7.098,2.526 6.969,2.475 6.813,2.475 L6.291,2.475 C6.075,2.475 5.9235,2.5245 5.8365,2.6235 C5.7495,2.7225 5.706,2.868 5.706,3.06 L5.706,3.69 L7.353,3.69 L7.353,3.015 Z"></path>
            <path d="M11.718,6.3 C11.412,6.3 11.178,6.201 11.016,6.003 C10.854,5.805 10.773,5.544 10.773,5.22 L10.773,2.475 L9.918,2.475 L9.918,1.8 L10.773,1.8 L10.773,0.72 L11.538,0.72 L11.538,1.8 L12.852,1.8 L12.852,2.475 L11.538,2.475 L11.538,5.265 C11.538,5.397 11.571,5.49 11.637,5.544 C11.703,5.598 11.805,5.625 11.943,5.625 L12.852,5.625 L12.852,6.3 L11.718,6.3 Z"></path>
            <path d="M17.568,6.3 C17.49,6.3 17.4045,6.276 17.3115,6.228 C17.2185,6.18 17.139,6.114 17.073,6.03 C16.935,6.21 16.752,6.3 16.524,6.3 L15.723,6.3 C15.267,6.3 14.9355,6.2085 14.7285,6.0255 C14.5215,5.8425 14.418,5.529 14.418,5.085 L14.418,4.905 C14.418,3.975 14.856,3.51 15.732,3.51 L16.848,3.51 L16.848,3.06 C16.848,2.874 16.791,2.73 16.677,2.628 C16.563,2.526 16.395,2.475 16.173,2.475 L14.778,2.475 L14.778,1.8 L16.083,1.8 C16.605,1.8 16.9905,1.914 17.2395,2.142 C17.4885,2.37 17.613,2.736 17.613,3.24 L17.613,5.4 C17.613,5.49 17.6475,5.5575 17.7165,5.6025 C17.7855,5.6475 17.901,5.67 18.063,5.67 L18.063,6.3 L17.568,6.3 Z M16.434,5.625 C16.614,5.625 16.728,5.583 16.776,5.499 C16.824,5.415 16.848,5.307 16.848,5.175 L16.848,4.185 L15.723,4.185 C15.567,4.185 15.438,4.236 15.336,4.338 C15.234,4.44 15.183,4.569 15.183,4.725 L15.183,5.175 C15.183,5.331 15.219,5.445 15.291,5.517 C15.363,5.589 15.477,5.625 15.633,5.625 L16.434,5.625 Z"></path>
          </g>
        </g>
      </g>
    </svg>
  );
}

export function Alpha() {
  return (
    <svg viewBox="0 0 33 11" version="1.1" xmlns="http://www.w3.org/2000/svg">
      <g stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
        <g>
          <rect
            fill="#BD372E"
            x="0"
            y="0"
            width="33"
            height="11"
            rx="5.5"
          ></rect>

          <g
            id="Alpha"
            transform="translate(5.405, 2.2)"
            fill="#FFFFFF"
            fillRule="nonzero"
          >
            <path d="M1.152,4.707 L0.801,6.3 L0,6.3 L1.521,0 L2.556,0 L4.05,6.3 L3.249,6.3 L2.907,4.707 L1.152,4.707 Z M2.763,4.032 L2.025,0.594 L1.296,4.032 L2.763,4.032 Z"></path>
            <path d="M7.173,6.3 C6.969,6.3 6.7905,6.228 6.6375,6.084 C6.4845,5.94 6.408,5.712 6.408,5.4 L6.408,0.675 L5.085,0.675 L5.085,0 L7.173,0 L7.173,5.355 C7.173,5.451 7.197,5.52 7.245,5.562 C7.293,5.604 7.374,5.625 7.488,5.625 L8.685,5.625 L8.685,6.3 L7.173,6.3 Z"></path>
            <path d="M10.818,1.8 L10.818,2.016 C11.004,1.872 11.244,1.8 11.538,1.8 L11.862,1.8 C12.39,1.8 12.777,1.9125 13.023,2.1375 C13.269,2.3625 13.392,2.73 13.392,3.24 L13.392,4.86 C13.392,5.364 13.2675,5.73 13.0185,5.958 C12.7695,6.186 12.384,6.3 11.862,6.3 L10.863,6.3 L10.863,7.83 L10.098,7.83 L10.098,1.8 L10.818,1.8 Z M11.448,2.475 C11.25,2.475 11.103,2.5275 11.007,2.6325 C10.911,2.7375 10.863,2.85 10.863,2.97 L10.863,5.625 L11.952,5.625 C12.174,5.625 12.342,5.574 12.456,5.472 C12.57,5.37 12.627,5.226 12.627,5.04 L12.627,3.06 C12.627,2.874 12.57,2.73 12.456,2.628 C12.342,2.526 12.174,2.475 11.952,2.475 L11.448,2.475 Z"></path>
            <path d="M15.723,0 L15.723,1.98 C15.903,1.86 16.128,1.8 16.398,1.8 L16.812,1.8 C17.298,1.8 17.6595,1.914 17.8965,2.142 C18.1335,2.37 18.252,2.736 18.252,3.24 L18.252,6.3 L17.487,6.3 L17.487,3.06 C17.487,2.88 17.4345,2.7375 17.3295,2.6325 C17.2245,2.5275 17.082,2.475 16.902,2.475 L16.308,2.475 C16.116,2.475 15.972,2.5245 15.876,2.6235 C15.78,2.7225 15.729,2.829 15.723,2.943 L15.723,6.3 L14.958,6.3 L14.958,0 L15.723,0 Z"></path>
            <path d="M22.788,6.3 C22.71,6.3 22.6245,6.276 22.5315,6.228 C22.4385,6.18 22.359,6.114 22.293,6.03 C22.155,6.21 21.972,6.3 21.744,6.3 L20.943,6.3 C20.487,6.3 20.1555,6.2085 19.9485,6.0255 C19.7415,5.8425 19.638,5.529 19.638,5.085 L19.638,4.905 C19.638,3.975 20.076,3.51 20.952,3.51 L22.068,3.51 L22.068,3.06 C22.068,2.874 22.011,2.73 21.897,2.628 C21.783,2.526 21.615,2.475 21.393,2.475 L19.998,2.475 L19.998,1.8 L21.303,1.8 C21.825,1.8 22.2105,1.914 22.4595,2.142 C22.7085,2.37 22.833,2.736 22.833,3.24 L22.833,5.4 C22.833,5.49 22.8675,5.5575 22.9365,5.6025 C23.0055,5.6475 23.121,5.67 23.283,5.67 L23.283,6.3 L22.788,6.3 Z M21.654,5.625 C21.834,5.625 21.948,5.583 21.996,5.499 C22.044,5.415 22.068,5.307 22.068,5.175 L22.068,4.185 L20.943,4.185 C20.787,4.185 20.658,4.236 20.556,4.338 C20.454,4.44 20.403,4.569 20.403,4.725 L20.403,5.175 C20.403,5.331 20.439,5.445 20.511,5.517 C20.583,5.589 20.697,5.625 20.853,5.625 L21.654,5.625 Z"></path>
          </g>
        </g>
      </g>
    </svg>
  );
}
