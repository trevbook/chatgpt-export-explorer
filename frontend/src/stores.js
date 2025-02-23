/**
 * Zustand store for managing global application state.
 * Provides state management for active tab selection and related functionality.
 */

/**
 * ===============
 * STORE SETUP
 * ===============
 * Below, we'll set up the Zustand store.
 */

import { create } from "zustand";

/**
 * ===============
 * STORE DEFINITION
 * ===============
 * We'll define the store and its actions here.
 */

/**
 * Creates a store for managing the active tab state.
 * Provides actions for getting and setting the active tab.
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
}));
