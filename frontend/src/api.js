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
