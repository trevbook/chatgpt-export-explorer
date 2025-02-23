/**
 * The Info Panel displays details about selected clusters or conversations in the Topic Map.
 * It provides contextual information based on user interactions with the visualization.
 *
 * @returns {JSX.Element} The Info Panel component
 */

/**
 * ===============
 * COMPONENT SETUP
 * ===============
 * Below, we'll set up the InfoPanel component.
 */
import { Box, Alert } from "@mantine/core";
import { IconInfoCircle } from "@tabler/icons-react";

/**
 * ===============
 * RENDERING LOGIC
 * ===============
 * We'll render the InfoPanel component here.
 */

export default function InfoPanel() {
  return (
    <Box
      h="100%"
      style={{
        display: "flex",
        flexDirection: "column",
        padding: "1rem",
      }}
    >
      <Alert
        variant="light"
        color="blue"
        title="Selection Details"
        icon={<IconInfoCircle />}
      >
        Click on a point in the visualization to see more information here.
      </Alert>
    </Box>
  );
}
