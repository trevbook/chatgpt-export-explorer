/**
 * The Scatterplot component displays the current scatterplot view using deck.gl.
 *
 * @param {Object[]} data - Array of point data with x, y, label, type, and size properties
 * @param {string} [colorControl='label'] - Property to use for controlling point colors
 * @returns {JSX.Element} The Scatterplot component
 */

/**
 * ===============
 * COMPONENT SETUP
 * ===============
 * Below, we'll set up the Scatterplot component.
 */
import { Box, useMantineTheme } from "@mantine/core";
import { useStore } from "../../store";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import { useState } from "react";

/**
 * ===============
 * RENDERING LOGIC
 * ===============
 * We'll render the Scatterplot component here.
 */

export default function Scatterplot({ data, colorControl = "label" }) {
  const theme = useMantineTheme();
  const colors = theme.colors;
  const [hoverInfo, setHoverInfo] = useState(null);

  // Get unique values for the color control
  const uniqueValues = [...new Set(data.map((d) => d[colorControl]))];

  // Create a color map using Mantine colors
  const colorMap = uniqueValues.reduce((acc, value, index) => {
    // Use different Mantine color palettes (blue, red, violet, green, yellow, etc.)
    const colorKeys = Object.keys(colors).filter(
      (key) => key !== "dark" && key !== "gray"
    );
    const colorKey = colorKeys[index % colorKeys.length];
    // Use shade 6 for a medium brightness
    acc[value] = colors[colorKey][6];
    return acc;
  }, {});

  // Calculate bounds of all points
  const bounds = data.reduce(
    (acc, point) => ({
      xMin: Math.min(acc.xMin, point.x),
      xMax: Math.max(acc.xMax, point.x),
      yMin: Math.min(acc.yMin, point.y),
      yMax: Math.max(acc.yMax, point.y),
    }),
    { xMin: Infinity, xMax: -Infinity, yMin: Infinity, yMax: -Infinity }
  );

  // Calculate center point
  const center = {
    longitude: (bounds.xMin + bounds.xMax) / 2,
    latitude: (bounds.yMin + bounds.yMax) / 2,
  };
  // Calculate appropriate zoom level based on the data bounds
  const xSpan = bounds.xMax - bounds.xMin;
  const ySpan = bounds.yMax - bounds.yMin;
  const maxSpan = Math.max(xSpan, ySpan);

  // Add padding factor to ensure points aren't right at the edges
  const padding = 0.4;
  const paddedSpan = maxSpan * padding;

  // Calculate zoom to fit the padded span
  // Using 2 as base since deck.gl uses power-of-2 zoom levels
  const zoom = Math.log2(360 / paddedSpan);

  const INITIAL_VIEW_STATE = {
    longitude: center.longitude,
    latitude: center.latitude,
    zoom: Math.max(0, Math.min(zoom - 1, 20)), // Subtract 1 to zoom out slightly, clamp between 0-20
    pitch: 0,
    bearing: 0,
    maxZoom: 20,
    minZoom: 0,
  };

  const layer = new ScatterplotLayer({
    id: "scatter",
    data,
    pickable: true,
    opacity: 0.8,
    stroked: true,
    filled: true,
    radiusScale: 1000,
    lineWidthMinPixels: 1,
    getPosition: (d) => [d.x, d.y, 0],
    getRadius: (d) => d.size || 1,
    getFillColor: (d) => {
      const value = d[colorControl];
      const hex = colorMap[value] || colors.gray[6];
      return [
        parseInt(hex.slice(1, 3), 16),
        parseInt(hex.slice(3, 5), 16),
        parseInt(hex.slice(5, 7), 16),
      ];
    },
    getLineColor: [0, 0, 0],
    onHover: (info) => setHoverInfo(info),
  });

  return (
    <Box style={{ height: "100%", position: "relative" }}>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={[layer]}
        getCursor={({ isDragging, isHovering }) => {
          if (isDragging) return "grabbing";
          if (isHovering) return "pointer";
          return "grab";
        }}
      />
      {hoverInfo?.object && (
        <div
          style={{
            position: "absolute",
            zIndex: 1,
            pointerEvents: "none",
            left: hoverInfo.x,
            top: hoverInfo.y,
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            color: "#fff",
            fontSize: "0.8em",
            padding: "4px 8px",
            borderRadius: "4px",
            transform: "translate(-50%, -100%)",
            marginTop: "-8px",
            width: "200px",
            whiteSpace: "normal",
            overflow: "hidden",
            wordWrap: "break-word",
            display: "flex",
            alignItems: "center", // Vertical centering
            justifyContent: "center", // Horizontal centering
            textAlign: "center", // Center text content
          }}
        >
          {hoverInfo.object.label}
        </div>
      )}
    </Box>
  );
}
