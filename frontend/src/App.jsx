import { useState, useEffect } from "react";
import { Tabs, Tab, Box, CircularProgress } from "@mui/material";
import { checkDataExists } from "./api";
import UploadTab from "./tabs/UploadTab";
import ScatterplotTab from "./tabs/ScatterplotTab";

export default function App() {
  const [activeTab, setActiveTab] = useState("upload");
  const [hasData, setHasData] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkData = async () => {
      try {
        const exists = await checkDataExists();
        setHasData(exists);
        // If no data exists, force user to upload tab
        if (!exists) {
          setActiveTab("upload");
        }
      } catch (error) {
        console.error("Error checking data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkData();
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
    <Box sx={{ width: "100%" }}>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="chat analysis tabs"
        >
          <Tab value="upload" label="Upload Data" />
          <Tab value="scatterplot" label="Scatterplot" disabled={!hasData} />
        </Tabs>
      </Box>

      <Box sx={{ p: 3 }}>
        {activeTab === "upload" && <UploadTab />}
        {activeTab === "scatterplot" && <ScatterplotTab />}
      </Box>
    </Box>
  );
}
