import { createTheme } from "@mui/material";

/**
 * Application theme configuration using Material UI's createTheme.
 * Defines typography, colors, and other theme properties.
 */
export const theme = createTheme({
  palette: {
    primary: {
      main: "#1a237e", // A deep royal blue color
    },
  },
  typography: {
    fontFamily: `"Instrument Sans", sans-serif`,
    fontSize: 14,
    fontWeightLight: 300,
    fontWeightRegular: 400,
    fontWeightMedium: 500,
  },
});
