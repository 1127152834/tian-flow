import { type OlightConfig } from "../config/types";

import { resolveServiceURL } from "./resolve-service-url";

declare global {
  interface Window {
    __olightConfig: OlightConfig;
  }
}

export async function loadConfig() {
  const res = await fetch(resolveServiceURL("./config"));
  const config = await res.json();
  return config;
}

export function getConfig(): OlightConfig {
  if (
    typeof window === "undefined" ||
    typeof window.__olightConfig === "undefined"
  ) {
    throw new Error("Config not loaded");
  }
  return window.__olightConfig;
}
