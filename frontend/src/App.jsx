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
import { Box, Loader, Tabs } from "@mantine/core";
import { useState } from "react";
import { useStore } from "./store";
import { useDataCheck } from "./hooks";
import TopicMapTab from "./tabs/TopicMapTab/TopicMapTab";
import ImportTab from "./tabs/ImportTab";
import WelcomeTab from "./tabs/WelcomeTab";

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

  const handleTabChange = (value) => {
    // Allow switching to the welcome tab even if no data exists
    if (!hasData && value !== "upload" && value !== "welcome") {
      return;
    }
    setActiveTab(value);
  };

  if (isLoading) {
    return (
      <Box
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <Loader />
      </Box>
    );
  }

  return (
    <Box
      style={{
        width: "100%",
        height: "95vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Tabs value={activeTab} onChange={handleTabChange}>
        <Tabs.List>
          <Tabs.Tab value="welcome">Welcome</Tabs.Tab>
          <Tabs.Tab value="upload">Import Data</Tabs.Tab>
          <Tabs.Tab value="topic-map" disabled={!hasData}>
            Topic Map
          </Tabs.Tab>
        </Tabs.List>
      </Tabs>

      <Box style={{ padding: "1rem", flexGrow: 1, height: 0 }}>
        {activeTab === "welcome" && <WelcomeTab />}
        {activeTab === "upload" && <ImportTab />}
        {activeTab === "topic-map" && <TopicMapTab />}
      </Box>
    </Box>
  );
}
