// Import the necessary libraries
import { useEffect } from "react";
import { Box } from "@mantine/core";
import { useStore } from "../../store";
import {
  getClusterSolutions,
  getClustersInSolution,
  getConversationsByClusterSolution,
} from "../../api";
import Scatterplot from "./Scatterplot";
import InfoPanel from "./InfoPanel";
import ControlPanel from "./ControlPanel";
import { transformClusterData } from "./utils";

// ===================
// RETURNING COMPONENT
// ===================
// Next up, we'll return the TopicMapTab component.

/**
 * The Topic Map Tab displays a visualization of conversation clusters.
 * It provides an interactive scatterplot view of either cluster centroids
 * or individual conversations, with controls for selecting different
 * clustering solutions and visualization modes.
 *
 * @returns {JSX.Element} The Topic Map Tab component
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
        const fetchPromise =
          scatterplotView === "cluster"
            ? getClustersInSolution(activeClusterSolutionId)
            : getConversationsByClusterSolution(activeClusterSolutionId);

        fetchPromise
          .then((data) => {
            console.log(`Received ${scatterplotView} data:`, data);
            setClusterDataCache(activeClusterSolutionId, scatterplotView, data);
          })
          .catch((err) => {
            console.error(`Error fetching ${scatterplotView} data:`, err);
          });
      }
    }
  }, [
    activeClusterSolutionId,
    scatterplotView,
    clusterDataCache,
    setClusterDataCache,
  ]);

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
      <ControlPanel />
      <Box style={{ display: "flex", gap: "1rem", height: "100%" }}>
        <Box
          style={{
            width: "75%",
            border: "1px solid black",
            // boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
          }}
        >
          {clusterData && (
            <Scatterplot
              data={transformClusterData(clusterData, scatterplotView)}
              colorControl="cluster"
            />
          )}
        </Box>
        <Box style={{ width: "25%" }}>
          <InfoPanel />
        </Box>
      </Box>
    </Box>
  );
}
