/**
 * This is the main application component that renders the app.
 *
 * @returns {JSX.Element} The App component
 */

/**
 * ===============
 * COMPONENT SETUP
 * ===============
 * Below, we'll set up the App component.
 */
import { Box, CircularProgress, Tab, Tabs } from "@mui/material";
import { useState } from "react";
import { useStore } from "./stores";
import { useDataCheck } from "./hooks";
import TopicMapTab from "./tabs/TopicMapTab";
import ImportTab from "./tabs/ImportTab";

/**
 * ===============
 * RENDERING LOGIC
 * ===============
 * We'll render the App component here.
 */

export default function App() {
  const activeTab = useStore((state) => state.activeTab);
  const setActiveTab = useStore((state) => state.setActiveTab);
  const hasData = useStore((state) => state.hasData);
  const [isLoading, setIsLoading] = useState(true);

  useDataCheck();

  // Once data check is complete, we can stop loading
  useState(() => {
    setIsLoading(false);
  }, []);

  const handleTabChange = (event, newValue) => {
    // Prevent switching away from upload tab if no data exists
    if (!hasData && newValue !== "upload") {
      return;
    }
    setActiveTab(newValue);
  };

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        width: "100%",
        height: "95vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="chat analysis tabs"
        >
          <Tab value="upload" label="Import Data" />
          <Tab value="topic-map" label="Topic Map" disabled={!hasData} />
        </Tabs>
      </Box>

      <Box sx={{ p: 3, flexGrow: 1, height: 0 }}>
        {activeTab === "upload" && <ImportTab />}
        {activeTab === "topic-map" && <TopicMapTab />}
      </Box>
    </Box>
  );
}
