import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ThemeProvider, createTheme } from "@mui/material";
import App from "./App.jsx";

const THEME = createTheme({
  typography: {
    fontFamily: `"Instrument Sans", sans-serif`,
    fontSize: 14,
    fontWeightLight: 300,
    fontWeightRegular: 400,
    fontWeightMedium: 500,
  },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ThemeProvider theme={THEME}>
      <App />
    </ThemeProvider>
  </StrictMode>
);
