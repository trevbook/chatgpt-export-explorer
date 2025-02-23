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
import { useStore } from "../../store";
import { getClusterSolutions, getClustersInSolution } from "../../api";
import Scatterplot from "./Scatterplot";

// Add this function above the component or in a separate utils file
function generateSyntheticData(numPoints = 100) {
  const types = ["primary", "secondary", "tertiary"];

  return Array.from({ length: numPoints }, (_, i) => ({
    x: (Math.random() - 0.5) * 10, // Random x between -5 and 5
    y: (Math.random() - 0.5) * 10, // Random y between -5 and 5
    label: `Point ${i + 1}`,
    type: types[Math.floor(Math.random() * types.length)],
    size: Math.random() * 3 + 0.5, // Random size between 0.5 and 3.5
    // Add some mock metadata
    cluster: Math.floor(Math.random() * 5), // Random cluster 0-4
    confidence: Math.random(), // Random confidence 0-1
    timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000), // Random date within last 30 days
  }));
}

function transformClusterData(clusterData, view) {
  if (!clusterData || !clusterData.clusters) return [];

  if (view === "cluster") {
    console.log(clusterData);
    // Return cluster centroids for cluster view
    return clusterData.clusters.map((cluster) => ({
      x: cluster.centroid_umap_x,
      y: cluster.centroid_umap_y,
      label: cluster.cluster_label,
      type: "cluster",
      size: cluster.cluster_size, // Size based on number of documents
      cluster: cluster.cluster_id,
      // Additional metadata
      description: cluster.cluster_description,
      tagCounts: cluster.tag_counts,
      similarity: cluster.mean_cosine_similarity,
    }));
  } else {
    // TODO: Return individual documents for document view
    return generateSyntheticData(clusterData.length);
  }
}

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
  const clusterDataCache = useStore((state) => state.clusterDataCache);
  const setClusterDataCache = useStore((state) => state.setClusterDataCache);

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

  useEffect(() => {
    if (activeClusterSolutionId !== null) {
      const cacheKey = `${activeClusterSolutionId}-${scatterplotView}`;
      if (!clusterDataCache[cacheKey]) {
        // Fetch data if not cached
        getClustersInSolution(activeClusterSolutionId)
          .then((data) => {
            console.log("Received cluster data:", data);
            setClusterDataCache(activeClusterSolutionId, scatterplotView, data);
          })
          .catch((err) => {
            console.error("Error fetching cluster data:", err);
          });
      }
    }
  }, [
    activeClusterSolutionId,
    scatterplotView,
    clusterDataCache,
    setClusterDataCache,
  ]);

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

  const cacheKey = `${activeClusterSolutionId}-${scatterplotView}`;
  const clusterData = clusterDataCache[cacheKey];

  return (
    <Box
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        height: "100%",
      }}
    >
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
      <Box style={{ display: "flex", gap: "1rem", height: "100%" }}>
        <Box style={{ width: "75%", border: "1px solid blue" }}>
          <Scatterplot
            data={
              clusterData
                ? transformClusterData(clusterData, scatterplotView)
                : generateSyntheticData(100) // Fallback data
            }
          />
        </Box>
        <Box style={{ width: "25%", border: "1px solid green" }}>info box</Box>
      </Box>
    </Box>
  );
}
