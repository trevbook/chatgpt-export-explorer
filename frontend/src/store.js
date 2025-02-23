/**
 * Zustand store for managing global application state.
 */

// Imports
import { create } from "zustand";

// ==============
// STORE CREATION
// ==============
// Below, we'll create a store for managing data for the application.

/**
 * The store for managing global application state.
 *
 * @type {import('zustand').StateCreator}
 */
export const useStore = create((set) => ({
  // ACTIVE TAB
  // The actively selected tab
  activeTab: "welcome",
  setActiveTab: (tab) => set({ activeTab: tab }),

  // HAS DATA
  // Flag indicating if data exists in the backend
  hasData: false,
  setHasData: (value) => set({ hasData: value }),

  // CLUSTER SOLUTION
  // Data related to the currently-selected / selectable clustering solutions
  activeClusterSolutionId: null,
  clusterSolutions: [],
  setClusterSolutions: (solutions) => set({ clusterSolutions: solutions }),
  setActiveClusterSolutionId: (id) => set({ activeClusterSolutionId: id }),

  // SCATTERPLOT VIEW
  // State to manage the selected scatterplot view
  scatterplotView: "cluster", // default to "cluster"
  setScatterplotView: (view) => set({ scatterplotView: view }),

  // CLUSTER DATA CACHE
  // State for caching cluster data based on solution ID and view
  clusterDataCache: {},
  /**
   * Sets the cluster data cache for a specific solution and view.
   *
   * @param {string} solutionId - The ID of the cluster solution.
   * @param {string} view - The view type (e.g., "cluster" or "document").
   * @param {object} data - The data to cache.
   */
  setClusterDataCache: (solutionId, view, data) =>
    set((state) => ({
      clusterDataCache: {
        ...state.clusterDataCache,
        [`${solutionId}-${view}`]: data,
      },
    })),
}));
