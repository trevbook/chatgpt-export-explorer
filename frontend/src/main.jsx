// Importing the necessary modules and components
import "@mantine/core/styles.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { MantineProvider } from "@mantine/core";
import { theme } from "./theme";
import App from "./App.jsx";

// Create and render the root React component
// We wrap the App in StrictMode for additional checks and warnings during development
// MantineProvider applies our custom theme to all Mantine components
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <MantineProvider theme={theme}>
      <App />
    </MantineProvider>
  </StrictMode>
);
