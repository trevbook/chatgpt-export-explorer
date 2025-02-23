// Importing the necessary dependencies
import { useEffect } from "react";
import { checkDataExists } from "./api";
import { useStore } from "./store";

/**
 * Hook for checking if data exists in the backend.
 * Automatically checks data existence when upload tab is active.
 * Updates global state with the result.
 */
export const useDataCheck = () => {
  const setHasData = useStore((state) => state.setHasData);
  const activeTab = useStore((state) => state.activeTab);

  useEffect(() => {
    const checkData = async () => {
      try {
        const exists = await checkDataExists();
        setHasData(exists);
      } catch (error) {
        console.error("Error checking data existence:", error);
        setHasData(false);
      }
    };

    if (activeTab === "upload" || activeTab === "welcome") {
      checkData();
    }
  }, [activeTab, setHasData]);
};
