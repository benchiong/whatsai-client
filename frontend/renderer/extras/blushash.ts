export const getClampedSize = (
  width: number,
  height: number,
  max: number,
  type: "width" | "height" | "all" = "all",
): { width: number; height: number } => {
  if (type === "all") {
    if (width >= height) type = "width";
    else if (height >= width) type = "height";
  }

  if (type === "width" && width > max)
    return { width: max, height: Math.round((height / width) * max) };

  if (type === "height" && height > max)
    return { width: Math.round((width / height) * max), height: max };

  return { width, height };
};
