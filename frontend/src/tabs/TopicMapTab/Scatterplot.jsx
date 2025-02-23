/**
 * The Scatterplot component displays the current scatterplot view using deck.gl.
 *
 * @returns {JSX.Element} The Scatterplot component
 */

/**
 * ===============
 * COMPONENT SETUP
 * ===============
 * Below, we'll set up the Scatterplot component.
 */
import { Box } from "@mantine/core";
import { useStore } from "../../store";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";

/**
 * ===============
 * RENDERING LOGIC
 * ===============
 * We'll render the Scatterplot component here.
 */

export default function Scatterplot() {
  // Generate some synthetic data points in a grid pattern
  const data = [];
  for (let x = -1; x <= 1; x += 0.2) {
    for (let y = -1; y <= 1; y += 0.2) {
      data.push({
        x: x,
        y: y,
        color: [
          Math.floor(Math.random() * 255),
          Math.floor(Math.random() * 255),
          Math.floor(Math.random() * 255),
        ],
      });
    }
  }

  const INITIAL_VIEW_STATE = {
    longitude: 0,
    latitude: 0,
    zoom: 2,
    pitch: 0,
    bearing: 0,
  };

  const layer = new ScatterplotLayer({
    id: "scatter",
    data,
    pickable: true,
    opacity: 0.8,
    stroked: true,
    filled: true,
    radiusScale: 6,
    radiusMinPixels: 3,
    radiusMaxPixels: 100,
    lineWidthMinPixels: 1,
    getPosition: (d) => [d.x, d.y, 0],
    getFillColor: (d) => d.color,
    getLineColor: [0, 0, 0],
  });

  return (
    <Box style={{ height: "600px", position: "relative" }}>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={[layer]}
      ></DeckGL>
    </Box>
  );
}
