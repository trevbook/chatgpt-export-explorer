"use client";
import { useState, useEffect } from "react";
import { Tabs, Tab, Box, CircularProgress } from "@mui/material";
import { checkDataExists } from "@/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState(0);
  const [hasData, setHasData] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkData = async () => {
      try {
        const exists = await checkDataExists();
        setHasData(exists);
        // If no data exists, force user to upload tab
        if (!exists) {
          setActiveTab(0);
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
    if (!hasData && newValue !== 0) {
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
          <Tab label="Upload Data" />
          <Tab label="Clusters" disabled={!hasData} />
          <Tab label="Analytics" disabled={!hasData} />
          <Tab label="Scatterplot" disabled={!hasData} />
        </Tabs>
      </Box>

      <Box sx={{ p: 3 }}>
        {activeTab === 0 && <div>Upload Data Tab Content</div>}
        {activeTab === 1 && <div>Clusters Tab Content</div>}
        {activeTab === 2 && <div>Analytics Tab Content</div>}
        {activeTab === 3 && <div>Scatterplot Tab Content</div>}
      </Box>
    </Box>
  );
}
