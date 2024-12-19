import { WidgetsType, WidgetUnionsType } from "../../data-type/widget";
import { Stack } from "@mantine/core";
import { widgetInfo2Widget } from "./index";
import React, { useState } from "react";

export function WidgetsRender({
  widgets,
  onChange,
  width = 400,
  height = 38,
  positionIndex,
}: {
  widgets: WidgetsType;
  onChange: (changedWidgets: WidgetsType) => void;
  width?: number;
  height?: number;
  positionIndex?: number | null;
}) {
  return (
    <Stack align="center" justify="space-between" gap="md" w={width}>
      {widgets.map((w, index) => {
        const { Widget, params, key } = widgetInfo2Widget(w) ?? {};
        params["paramName"] = key;
        if (!Widget) {
          return <></>;
        }
        return (
          <Widget
            {...params}
            key={key}
            onChange={(value) => {
              let newWidgets: WidgetsType = [...widgets];
              newWidgets[index] = {
                ...widgets[index],
                value: value,
              } as WidgetUnionsType;
              onChange(newWidgets);
            }}
            height={height}
            positionIndex={positionIndex}
          />
        );
      })}
    </Stack>
  );
}
