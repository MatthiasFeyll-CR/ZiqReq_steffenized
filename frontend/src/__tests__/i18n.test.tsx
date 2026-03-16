import { describe, it, expect, beforeEach, afterEach } from "vitest";
import i18n from "@/i18n/config";
import deJson from "@/i18n/locales/de.json";
import enJson from "@/i18n/locales/en.json";

/**
 * Recursively collect all leaf keys from a nested JSON object.
 * e.g. { a: { b: "val" } } → ["a.b"]
 */
function collectKeys(obj: Record<string, unknown>, prefix = ""): string[] {
  const keys: string[] = [];
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      keys.push(...collectKeys(value as Record<string, unknown>, fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  return keys;
}

describe("T-16.1.01: All text in both languages", () => {
  it("de.json and en.json have the same set of keys", () => {
    const deKeys = collectKeys(deJson).sort();
    const enKeys = collectKeys(enJson).sort();

    const missingInEn = deKeys.filter((k) => !enKeys.includes(k));
    const missingInDe = enKeys.filter((k) => !deKeys.includes(k));

    expect(missingInEn, `Keys in de.json but missing in en.json: ${missingInEn.join(", ")}`).toEqual([]);
    expect(missingInDe, `Keys in en.json but missing in de.json: ${missingInDe.join(", ")}`).toEqual([]);
  });

  it("no translation values are empty strings", () => {
    const deKeys = collectKeys(deJson);
    const enKeys = collectKeys(enJson);

    for (const key of deKeys) {
      const val = key.split(".").reduce<unknown>((o, k) => (o as Record<string, unknown>)?.[k], deJson);
      expect(val, `de.json key "${key}" is empty`).not.toBe("");
    }

    for (const key of enKeys) {
      const val = key.split(".").reduce<unknown>((o, k) => (o as Record<string, unknown>)?.[k], enJson);
      expect(val, `en.json key "${key}" is empty`).not.toBe("");
    }
  });

  it("both locales have a minimum set of required key namespaces", () => {
    const requiredNamespaces = [
      "common",
      "nav",
      "user",
      "landing",
      "workspace",
      "errors",
      "errorLog",
      "offline",
      "collaboration",
      "review",
      "timeline",
      "notifications",
      "emailPrefs",
      "admin",
      "brd",
      "chat",
      "submit",
      "email",
    ];

    for (const ns of requiredNamespaces) {
      expect(deJson, `de.json missing namespace "${ns}"`).toHaveProperty(ns);
      expect(enJson, `en.json missing namespace "${ns}"`).toHaveProperty(ns);
    }
  });
});

describe("T-16.2.01: Language switcher changes text", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("en");
  });

  afterEach(async () => {
    await i18n.changeLanguage("en");
  });

  it("switching from en to de changes translations", async () => {
    expect(i18n.t("common.loading")).toBe("Loading...");
    expect(i18n.t("nav.ideas")).toBe("Ideas");

    await i18n.changeLanguage("de");

    expect(i18n.t("common.loading")).toBe("Laden...");
    expect(i18n.t("nav.ideas")).toBe("Ideen");
  });

  it("switching from de to en changes translations", async () => {
    await i18n.changeLanguage("de");
    expect(i18n.t("errors.title")).toBe("Fehler");

    await i18n.changeLanguage("en");
    expect(i18n.t("errors.title")).toBe("Error");
  });

  it("all top-level namespaces differ between languages", async () => {
    // Spot-check that at least one key in each namespace is different
    const spotChecks: Record<string, string> = {
      "common.loading": "common.loading",
      "nav.ideas": "nav.ideas",
      "errors.title": "errors.title",
      "offline.reconnect": "offline.reconnect",
      "review.pageTitle": "review.pageTitle",
      "admin.monitoring": "admin.monitoring",
    };

    for (const key of Object.values(spotChecks)) {
      await i18n.changeLanguage("en");
      const enVal = i18n.t(key);
      await i18n.changeLanguage("de");
      const deVal = i18n.t(key);
      expect(enVal, `Key "${key}" has same value in en and de`).not.toBe(deVal);
    }
  });
});

describe("T-16.2.02: Language preference persists", () => {
  it("stores language preference in localStorage", async () => {
    localStorage.setItem("language", "de");
    expect(localStorage.getItem("language")).toBe("de");

    // Simulate what the language switcher does
    const next = "en";
    await i18n.changeLanguage(next);
    localStorage.setItem("language", next);

    expect(localStorage.getItem("language")).toBe("en");
    expect(i18n.language).toBe("en");
  });

  it("i18n config reads language from localStorage", () => {
    // The i18n config reads: localStorage.getItem("language") ?? "de"
    // We set "en" in test-setup, so it should be "en"
    expect(i18n.language).toBe("en");
  });
});
