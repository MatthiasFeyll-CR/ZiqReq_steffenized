import "@testing-library/jest-dom/vitest";
import i18n from "@/i18n/config";

// Initialize i18n for tests — default to English
i18n.changeLanguage("en");
localStorage.setItem("language", "en");

// jsdom does not implement URL.createObjectURL / revokeObjectURL
if (typeof URL.createObjectURL === "undefined") {
  URL.createObjectURL = () => "blob:mock";
  URL.revokeObjectURL = () => {};
}

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});
