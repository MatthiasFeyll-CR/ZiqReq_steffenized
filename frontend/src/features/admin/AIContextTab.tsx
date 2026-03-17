import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  fetchFacilitatorContext,
  patchFacilitatorContext,
  fetchCompanyContext,
  patchCompanyContext,
} from "@/api/admin";
import type { ContextType } from "@/api/admin";

const CONTEXT_TYPES: { value: ContextType; label: string }[] = [
  { value: "global", label: "Global" },
  { value: "software", label: "Software" },
  { value: "non_software", label: "Non-Software" },
];

export function AIContextTab() {
  const { t } = useTranslation();
  const [activeType, setActiveType] = useState<ContextType>("global");

  const [facilitatorContent, setFacilitatorContent] = useState("");
  const [facilitatorLoading, setFacilitatorLoading] = useState(true);
  const [facilitatorSaving, setFacilitatorSaving] = useState(false);

  const [sectionsText, setSectionsText] = useState("");
  const [freeText, setFreeText] = useState("");
  const [companyLoading, setCompanyLoading] = useState(true);
  const [companySaving, setCompanySaving] = useState(false);

  const loadData = useCallback(
    (contextType: ContextType) => {
      setFacilitatorLoading(true);
      setCompanyLoading(true);

      fetchFacilitatorContext(contextType)
        .then((data) => setFacilitatorContent(data.content))
        .catch((err) =>
          toast.error(`${t("admin.failedLoadFacilitator")}: ${err.message}`),
        )
        .finally(() => setFacilitatorLoading(false));

      fetchCompanyContext(contextType)
        .then((data) => {
          setSectionsText(JSON.stringify(data.sections, null, 2));
          setFreeText(data.free_text);
        })
        .catch((err) =>
          toast.error(`${t("admin.failedLoadCompany")}: ${err.message}`),
        )
        .finally(() => setCompanyLoading(false));
    },
    [t],
  );

  useEffect(() => {
    loadData(activeType);
  }, [activeType, loadData]);

  function handleTypeChange(type: ContextType) {
    if (type === activeType) return;
    setActiveType(type);
  }

  async function handleFacilitatorSave() {
    setFacilitatorSaving(true);
    try {
      await patchFacilitatorContext(facilitatorContent, activeType);
      toast.success(t("admin.facilitatorSaved"));
    } catch (err) {
      toast.error(
        `${t("admin.failedSaveFacilitator")}: ${(err as Error).message}`,
      );
    } finally {
      setFacilitatorSaving(false);
    }
  }

  async function handleCompanySave() {
    let sections: Record<string, unknown>;
    try {
      sections = JSON.parse(sectionsText);
    } catch {
      toast.error(t("admin.invalidJson"));
      return;
    }
    setCompanySaving(true);
    try {
      await patchCompanyContext(sections, freeText, activeType);
      toast.success(t("admin.companySaved"));
    } catch (err) {
      toast.error(
        `${t("admin.failedSaveCompany")}: ${(err as Error).message}`,
      );
    } finally {
      setCompanySaving(false);
    }
  }

  return (
    <div className="space-y-8 py-6">
      {/* Segmented Control */}
      <nav
        className="flex border-b border-border"
        role="tablist"
        data-testid="context-type-tabs"
      >
        {CONTEXT_TYPES.map(({ value, label }) => (
          <button
            key={value}
            role="tab"
            aria-selected={activeType === value}
            data-testid={`context-tab-${value}`}
            onClick={() => handleTypeChange(value)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeType === value
                ? "border-b-2 border-primary text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      {/* Facilitator Context */}
      <section className="space-y-3">
        <h3 className="text-lg font-medium">{t("admin.facilitatorTitle")}</h3>
        {facilitatorLoading ? (
          <p className="text-sm text-muted-foreground">
            {t("common.loading")}
          </p>
        ) : (
          <>
            <Textarea
              value={facilitatorContent}
              onChange={(e) => setFacilitatorContent(e.target.value)}
              rows={8}
              placeholder={t("admin.facilitatorPlaceholder")}
              data-testid="facilitator-textarea"
            />
            <Button
              onClick={handleFacilitatorSave}
              disabled={facilitatorSaving}
            >
              {facilitatorSaving
                ? t("common.saving")
                : t("admin.saveFacilitator")}
            </Button>
          </>
        )}
      </section>

      {/* Company Context */}
      <section className="space-y-3">
        <h3 className="text-lg font-medium">{t("admin.companyTitle")}</h3>
        {companyLoading ? (
          <p className="text-sm text-muted-foreground">
            {t("common.loading")}
          </p>
        ) : (
          <>
            <div className="space-y-2">
              <label className="text-sm font-medium">
                {t("admin.sectionsJson")}
              </label>
              <Textarea
                value={sectionsText}
                onChange={(e) => setSectionsText(e.target.value)}
                rows={10}
                placeholder='{"section_name": "content"}'
                className="font-mono text-xs"
                data-testid="sections-textarea"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">
                {t("admin.freeText")}
              </label>
              <Textarea
                value={freeText}
                onChange={(e) => setFreeText(e.target.value)}
                rows={6}
                placeholder={t("admin.freeTextPlaceholder")}
                data-testid="freetext-textarea"
              />
            </div>
            <Button onClick={handleCompanySave} disabled={companySaving}>
              {companySaving ? t("common.saving") : t("admin.saveCompany")}
            </Button>
          </>
        )}
      </section>
    </div>
  );
}
