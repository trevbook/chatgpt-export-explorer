/**
 * The Upload Tab handles the upload of data files to the backend.
 *
 * @returns {JSX.Element} The Upload Tab component
 */

/**
 * ===============
 * COMPONENT SETUP
 * ===============
 * Below, we'll set up the UploadTab component.
 */
import { useState, useEffect, useCallback } from "react";
import { Box, Paper, Text, Progress } from "@mantine/core";
import {
  checkDataExists,
  uploadConversations,
  getProcessingStatus,
} from "../api";
import { useStore } from "../stores";

const UploadBox = ({ children, ...props }) => (
  <Paper
    {...props}
    p="xl"
    style={(theme) => ({
      border: `2px dashed ${theme.primaryColor}`,
      borderRadius: theme.radius.md,
      cursor: "pointer",
      backgroundColor: "transparent",
      textAlign: "center",
      "&:hover": {
        backgroundColor: theme.colors.gray[0],
      },
    })}
  >
    {children}
  </Paper>
);

/**
 * ===============
 * RENDERING LOGIC
 * ===============
 * We'll render the UploadTab component here.
 */

export default function ImportTab() {
  const { hasData, setHasData } = useStore();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState("");

  useEffect(() => {
    const checkData = async () => {
      const result = await checkDataExists();
      setHasData(result);
    };
    checkData();
  }, [setHasData]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const startPollingStatus = useCallback(() => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await getProcessingStatus();
        setUploadProgress(status.progress);
        setUploadStatus(status.message);

        if (status.status === "complete" || status.status === "error") {
          clearInterval(pollInterval);
          const hasDataNow = await checkDataExists();
          setHasData(hasDataNow);
          setIsUploading(false);
        }
      } catch (error) {
        console.error("Error polling status:", error);
        clearInterval(pollInterval);
        setIsUploading(false);
      }
    }, 1000);

    return pollInterval;
  }, [setHasData]);

  const handleFileUpload = useCallback(
    async (file) => {
      try {
        setIsUploading(true);
        setUploadProgress(0);
        setUploadStatus("Starting upload...");

        await uploadConversations(file);
        const pollInterval = startPollingStatus();

        // Cleanup polling on component unmount
        return () => clearInterval(pollInterval);
      } catch (error) {
        console.error("Error uploading file:", error);
        setIsUploading(false);
        setUploadStatus("Upload failed!");
      }
    },
    [startPollingStatus]
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer?.files;
      if (files?.[0]) {
        handleFileUpload(files[0]);
      }
    },
    [handleFileUpload]
  );

  const handleClick = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = (e) => {
      const file = e.target?.files?.[0];
      if (file) {
        handleFileUpload(file);
      }
    };
    input.click();
  };

  return (
    <Box
      h="100%"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "1rem",
      }}
    >
      {hasData ? (
        <Text size="xl" c="blue">
          You've got processed data! 😊
        </Text>
      ) : isUploading ? (
        <>
          <Progress value={uploadProgress} size="xl" radius="xl" />
          <Text>{uploadStatus}</Text>
          <Text>Progress: {uploadProgress}%</Text>
        </>
      ) : (
        <UploadBox
          onClick={handleClick}
          onDragEnter={handleDragIn}
          onDragLeave={handleDragOut}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            backgroundColor: isDragging
              ? "var(--mantine-color-gray-0)"
              : "transparent",
          }}
        >
          <Text size="lg">Drag & Drop to Upload conversations.json</Text>
        </UploadBox>
      )}
    </Box>
  );
}
