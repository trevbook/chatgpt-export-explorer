/**
 * API utilities for interacting with the ChatGPT Explorer backend.
 * Provides functions for checking data existence, uploading files,
 * and retrieving clustering results.
 */

/**
 * ===============
 * API SETUP
 * ===============
 * Below, we'll set up the API utilities.
 */

// Various imports
import axios from "axios";

// Extracting the API URL from the environment
const API_URL = import.meta.env.VITE_API_URL;

/**
 * ===============
 * API FUNCTIONS
 * ===============
 * We'll define the API functions here.
 */

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
