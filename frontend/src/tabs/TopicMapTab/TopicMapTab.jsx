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
import { Box, Select, Radio, Group, Text } from "@mantine/core";
import { useStore } from "../../stores";
import { getClusterSolutions } from "../../api";
import Scatterplot from "./Scatterplot";

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
  const scatterplotView = useStore((state) => state.scatterplotView);
  const setScatterplotView = useStore((state) => state.setScatterplotView);

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

  const radioCards = [
    {
      value: "cluster",
      label: "Cluster View",
      description: "View the scatterplot with clusters highlighted.",
    },
    {
      value: "document",
      label: "Document View",
      description:
        "View the scatterplot with individual documents highlighted.",
    },
  ];

  const cards = radioCards.map((item) => (
    <Radio.Card
      style={{
        position: "relative",
        padding: "var(--mantine-spacing-sm)",
        transition: "border-color 150ms ease",
        borderColor:
          item.value === scatterplotView
            ? "var(--mantine-primary-color-filled)"
            : undefined,
        backgroundColor:
          item.value === scatterplotView
            ? "var(--mantine-color-gray-0)"
            : undefined,
      }}
      radius="md"
      value={item.value}
      key={item.value}
    >
      <Group wrap="nowrap" align="flex-start">
        <Radio.Indicator />
        <div>
          <Text
            style={{
              fontWeight: "bold",
              fontSize: "var(--mantine-font-size-md)",
              lineHeight: 1.2,
              color: "var(--mantine-color-bright)",
            }}
          >
            {item.label}
          </Text>
          <Text
            style={{
              marginTop: "4px",
              color: "var(--mantine-color-dimmed)",
              fontSize: "var(--mantine-font-size-xs)",
            }}
          >
            {item.description}
          </Text>
        </div>
      </Group>
    </Radio.Card>
  ));

  return (
    <Box style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <Box style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <Select
          label={<strong>Clustering Solution</strong>}
          placeholder="Select a solution"
          data={clusterSolutions.map((solution) => ({
            value: solution.cluster_solution_id,
            label: `${solution.cluster_solution_id} (${solution.n_clusters} clusters)`,
          }))}
          value={activeClusterSolutionId}
          onChange={handleSolutionChange}
          clearable={false}
          style={{ flex: 1 }}
        />

        <Radio.Group
          value={scatterplotView}
          onChange={setScatterplotView}
          style={{ flex: 2 }}
        >
          <Group pt="md" gap="xs" direction="row" wrap="nowrap">
            {cards}
          </Group>
        </Radio.Group>
      </Box>
      <Scatterplot />
    </Box>
  );
}
