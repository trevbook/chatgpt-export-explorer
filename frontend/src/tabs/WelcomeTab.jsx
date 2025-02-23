/**
 * The Welcome Tab provides an introduction to the ChatGPT Export Explorer application.
 * It offers a brief overview of the app's functionality and purpose.
 *
 * @returns {JSX.Element} The Welcome Tab component
 */

/**
 * ===============
 * COMPONENT SETUP
 * ===============
 * Below, we'll set up the WelcomeTab component.
 */
import { Box, Text } from "@mantine/core";

/**
 * ===============
 * RENDERING LOGIC
 * ===============
 * We'll render the WelcomeTab component here.
 */

export default function WelcomeTab() {
  return (
    <Box
      h="100%"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: "1rem",
      }}
    >
      <Text size="xl" weight={700}>
        Welcome to ChatGPT Export Explorer
      </Text>
      <Text size="md" mt="md" style={{ maxWidth: "45%" }}>
        ChatGPT Export Explorer is a local web application for analyzing and
        visualizing ChatGPT conversation history. The app processes exported
        ChatGPT JSON files, performs semantic clustering analysis, and provides
        interactive visualizations and analytics of conversation patterns.
      </Text>
    </Box>
  );
}
