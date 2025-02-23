// Imports
import { createTheme } from "@mantine/core";

/**
 * Application theme configuration using Mantine's createTheme.
 * Defines typography, colors, and other theme properties.
 */
export const theme = createTheme({
  primaryColor: "indigo",
  colors: {
    indigo: [
      "#E8EAF6",
      "#C5CAE9",
      "#9FA8DA",
      "#7986CB",
      "#5C6BC0",
      "#3F51B5",
      "#3949AB",
      "#303F9F",
      "#283593",
      "#1A237E",
    ],
  },
  fontFamily: "Instrument Sans, sans-serif",
  fontSizes: {
    xs: "12px",
    sm: "14px",
    md: "16px",
    lg: "18px",
    xl: "20px",
  },
  fontWeights: {
    light: 300,
    regular: 400,
    medium: 500,
  },
});
