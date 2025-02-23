/**
 * The Scatterplot Tab displays a visualization of conversation clusters.
 *
 * @returns {JSX.Element} The Scatterplot Tab component
 */

/**
 * ===============
 * COMPONENT SETUP
 * ===============
 * Below, we'll set up the ScatterplotTab component.
 */
import { useEffect } from "react";
import { Box, Select } from "@mantine/core";
import { useStore } from "../stores";
import { getClusterSolutions } from "../api";

/**
 * ===============
 * RENDERING LOGIC
 * ===============
 * We'll render the ScatterplotTab component here.
 */

export default function TopicMapTab() {
  const clusterSolutions = useStore((state) => state.clusterSolutions);
  const activeClusterSolutionId = useStore(
    (state) => state.activeClusterSolutionId
  );
  const setClusterSolutions = useStore((state) => state.setClusterSolutions);
  const setActiveClusterSolutionId = useStore(
    (state) => state.setActiveClusterSolutionId
  );

  useEffect(() => {
    // Fetch cluster solutions if we don't have any
    if (clusterSolutions.length === 0) {
      getClusterSolutions()
        .then((data) => {
          setClusterSolutions(data);
          setActiveClusterSolutionId(data[0].cluster_solution_id);
        })
        .catch((err) => {
          console.error("Error fetching cluster solutions:", err);
        });
    }
  }, [clusterSolutions.length, setClusterSolutions]);

  const handleSolutionChange = (value) => {
    setActiveClusterSolutionId(value);
  };

  return (
    <Box>
      <Select
        label="Clustering Solution"
        placeholder="Select a solution"
        data={clusterSolutions.map((solution) => ({
          value: solution.cluster_solution_id,
          label: `${solution.cluster_solution_id} (${solution.n_clusters} clusters)`,
        }))}
        value={activeClusterSolutionId || ""}
        onChange={handleSolutionChange}
        style={{ minWidth: 200, marginBottom: "1rem" }}
      />
    </Box>
  );
}
