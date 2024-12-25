import { WidgetInt } from "./WidgetInt";
import { WidgetFloat } from "./WidgetFloat";
import { WidgetCombo } from "./WidgetCombo";
import { WidgetSeed } from "./WidgetSeed";
import { WidgetText } from "./WidgetText";
import { WidgetModelCombo } from "./WidgetModelCombo";
import { WidgetImage } from "./WidgetImage";
import { GroupedWidgets } from "./GroupedWidgets";
import { SwitchableWidgets } from "./SwitchableWidgets";
import { WidgetBool } from "./WidgetBool";

export type WidgetNameComponentMapType = {
  [key: string]: any;
};
export const WidgetNameComponentMap: WidgetNameComponentMapType = {
  BoolWidget: WidgetBool,
  IntWidget: WidgetInt,
  FloatWidget: WidgetFloat,
  ComboWidget: WidgetCombo,
  SeedWidget: WidgetSeed,
  TextWidget: WidgetText,
  ModelComboWidget: WidgetModelCombo,
  ImageWidget: WidgetImage,
  SwitchableWidgets: SwitchableWidgets,
  GroupedWidgets: GroupedWidgets,
};

export type WidgetAndParams = {
  key: string;
  widgetType: string;
  Widget:
    | typeof WidgetBool
    | typeof WidgetInt
    | typeof WidgetFloat
    | typeof WidgetCombo
    | typeof WidgetSeed
    | typeof WidgetText
    | typeof WidgetModelCombo
    | typeof WidgetImage
    | typeof SwitchableWidgets
    | typeof GroupedWidgets;
  params: any;
  widgetInfo: any;
};
// Given widgetInfo, return the corresponding Widget and params and other useful info.
export function widgetInfo2Widget(widgetInfo: any): WidgetAndParams | null {
  if (!widgetInfo) {
    return null;
  }
  const widgetType = widgetInfo["widget_type"];
  const Widget = WidgetNameComponentMap[widgetType];
  if (!Widget) {
    return null;
  }

  let params = {};
  switch (Widget) {
    case WidgetBool:
      params = {
        text: widgetInfo["display_name"],
        value: widgetInfo["value"],
      };
      break;
    case WidgetInt:
      params = {
        text: widgetInfo["display_name"],
        value: widgetInfo["value"],
        step: widgetInfo["step"],
        max: widgetInfo["max"],
        min: widgetInfo["min"],
      };
      break;
    case WidgetFloat:
      params = {
        text: widgetInfo["display_name"],
        value: widgetInfo["value"],
        step: widgetInfo["step"],
        max: widgetInfo["max"],
        min: widgetInfo["min"],
        round: widgetInfo["round"],
      };
      break;
    case WidgetCombo:
      params = {
        text: widgetInfo["display_name"],
        value: widgetInfo["value"],
        values: widgetInfo["values"],
      };
      break;

    case WidgetSeed:
      params = {
        text: widgetInfo["display_name"],
        defaultValue: widgetInfo["value"],
        max: widgetInfo["max"],
      };
      break;

    case WidgetText:
      params = {
        text: widgetInfo["display_name"],
        value: widgetInfo["value"],
      };
      break;
    case WidgetModelCombo:
      params = {
        text: widgetInfo["display_name"],
        defaultModelId: widgetInfo["value"],
        funcName: widgetInfo["values_function_name"],
        paramName: widgetInfo["param_name"],
        optional: widgetInfo["optional"],
      };
      break;
    case WidgetImage:
      params = {
        text: widgetInfo["display_name"],
        defaultImage: widgetInfo["value"],
      };
      break;
    case SwitchableWidgets:
      params = {
        text: widgetInfo["display_name"],
        values: widgetInfo["values"],
        value: widgetInfo["value"],
      };
      break;
    case GroupedWidgets:
      params = {
        text: widgetInfo["display_name"],
        widgets: widgetInfo["value"],
      };
      break;
    default:
      params = {};
  }

  return {
    key: widgetInfo["display_name"],
    widgetType: widgetInfo["widget_type"],
    Widget: Widget,
    params: params,
    widgetInfo: widgetInfo,
    visible: widgetInfo["visible"],
  };
}
