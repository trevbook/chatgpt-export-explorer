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
import { Typography, Box, Paper } from "@mui/material";
import { styled } from "@mui/material/styles";
import { checkDataExists } from "../api";

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
  const [hasData, setHasData] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const checkData = async () => {
      const result = await checkDataExists();
      setHasData(result);
    };
    checkData();
  }, []);

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

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer?.files;
    if (files?.[0]) {
      console.log("File dropped:", files[0]);
      // TODO: Handle file upload
    }
  }, []);

  const handleClick = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = (e) => {
      const file = e.target?.files?.[0];
      if (file) {
        console.log("File selected:", file);
        // TODO: Handle file upload
      }
    };
    input.click();
  };

  return (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {hasData ? (
        <Typography variant="h5" color="primary">
          You've got data uploaded! 😊
        </Typography>
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
