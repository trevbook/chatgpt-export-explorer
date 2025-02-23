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
import { Typography, Box, Paper, CircularProgress } from "@mui/material";
import { styled } from "@mui/material/styles";
import {
  checkDataExists,
  uploadConversations,
  getProcessingStatus,
} from "../api";
import { useStore } from "../stores";

const UploadBox = styled(Paper)(({ theme }) => ({
  border: `2px dashed ${theme.palette.primary.main}`,
  borderRadius: theme.spacing(2),
  padding: theme.spacing(4),
  textAlign: "center",
  cursor: "pointer",
  backgroundColor: "transparent",
  transition: "background-color 0.3s ease",
  "&:hover": {
    backgroundColor: theme.palette.action.hover,
  },
}));

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
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 2,
      }}
    >
      {hasData ? (
        <Typography variant="h5" color="primary">
          You've got data uploaded! 😊
        </Typography>
      ) : isUploading ? (
        <>
          <CircularProgress variant="determinate" value={uploadProgress} />
          <Typography>{uploadStatus}</Typography>
          <Typography>Progress: {uploadProgress}%</Typography>
        </>
      ) : (
        <UploadBox
          elevation={0}
          onClick={handleClick}
          onDragEnter={handleDragIn}
          onDragLeave={handleDragOut}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          sx={{
            backgroundColor: isDragging ? "action.hover" : "transparent",
          }}
        >
          <Typography variant="h6">
            Drag & Drop to Upload conversations.json
          </Typography>
        </UploadBox>
      )}
    </Box>
  );
}
