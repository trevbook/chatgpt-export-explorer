/**
 * The Scatterplot component displays the current scatterplot view.
 *
 * @returns {JSX.Element} The Scatterplot component
 */

/**
 * ===============
 * COMPONENT SETUP
 * ===============
 * Below, we'll set up the Scatterplot component.
 */
import { Box, Text } from "@mantine/core";
import { useStore } from "../../stores";

/**
 * ===============
 * RENDERING LOGIC
 * ===============
 * We'll render the Scatterplot component here.
 */

export default function Scatterplot() {
  const scatterplotView = useStore((state) => state.scatterplotView);

  return (
    <Box style={{ padding: "1rem" }}>
      <Text>scatterplot view = {scatterplotView}</Text>
    </Box>
  );
}
