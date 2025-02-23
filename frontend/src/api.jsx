/**
 * API utilities for interacting with the ChatGPT Explorer backend.
 * Provides functions for checking data existence, uploading files,
 * and retrieving clustering results.
 */

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

export const checkDataExists = async () => {
  try {
    const response = await axios.get(`${API_URL}/has-data`);
    return response.data;
  } catch (error) {
    console.error("Error checking if data exists:", error);
    return false;
  }
};
