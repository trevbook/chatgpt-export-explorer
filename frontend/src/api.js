/**
 * API client for the ChatGPT Explorer backend.
 * Provides functions for data management, file uploads, and clustering operations.
 */

// Imports
import axios from "axios";

// Extract environment variables
const API_URL = import.meta.env.VITE_API_URL;

// =============
// API FUNCTIONS
// =============
// Below, we'll define a number of functions that interact with the backend API.

/**
 * Checks if any conversation data exists in the backend database.
 * Makes a GET request to the /has-data endpoint to verify data presence.
 *
 * @async
 * @returns {Promise<boolean>} True if data exists, false otherwise or if error occurs
 */
export const checkDataExists = async () => {
  try {
    const response = await axios.get(`${API_URL}/has-data`);
    return response.data;
  } catch (error) {
    console.error("Error checking if data exists:", error);
    return false;
  }
};

/**
 * Uploads a conversations.json file to the backend for processing.
 *
 * @async
 * @param {File} file - The conversations.json file to upload
 * @returns {Promise<Object>} The initial processing status
 */
export const uploadConversations = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(`${API_URL}/upload`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

/**
 * Gets the current processing status from the backend.
 *
 * @async
 * @returns {Promise<Object>} The current processing status
 */
export const getProcessingStatus = async () => {
  const response = await axios.get(`${API_URL}/processing-status`);
  return response.data;
};

/**
 * Fetches the available clustering solutions from the backend.
 * Makes a GET request to /conversations/cluster-solutions to get all cluster solutions.
 *
 * @async
 * @returns {Promise<Object[]>} Array of cluster solutions, each containing cluster_solution_id and n_clusters
 * @throws {Error} If no conversation data exists or if request fails
 */
export const getClusterSolutions = async () => {
  const response = await axios.get(
    `${API_URL}/conversations/cluster-solutions`
  );
  return response.data;
};

/**
 * Fetches the clusters for a specific clustering solution from the backend.
 * Makes a GET request to /conversations/clusters-in-solution/:clusteringSolutionId to get clusters.
 *
 * @async
 * @param {string} clusteringSolutionId - The ID of the clustering solution
 * @returns {Promise<Object>} Clustering results for the specified solution
 * @throws {Error} If no conversation data exists or if request fails
 */
export const getClustersInSolution = async (clusteringSolutionId) => {
  try {
    const response = await axios.get(
      `${API_URL}/conversations/clusters-in-solution/${clusteringSolutionId}`
    );
    return response.data;
  } catch (error) {
    console.error(
      `Error fetching clusters for solution ${clusteringSolutionId}:`,
      error
    );
    throw error;
  }
};

/**
 * Fetches all conversations for a specific clustering solution, including their cluster assignments.
 * Makes a GET request to /conversations/by-cluster-solution/:clusteringSolutionId.
 *
 * @async
 * @param {string} clusteringSolutionId - The ID of the clustering solution
 * @returns {Promise<Object[]>} Array of conversations with cluster assignments
 * @throws {Error} If no conversation data exists or if request fails
 */
export const getConversationsByClusterSolution = async (
  clusteringSolutionId
) => {
  try {
    const response = await axios.get(
      `${API_URL}/conversations/by-cluster-solution/${clusteringSolutionId}`
    );
    return response.data;
  } catch (error) {
    console.error(
      `Error fetching conversations for cluster solution ${clusteringSolutionId}:`,
      error
    );
    throw error;
  }
};
