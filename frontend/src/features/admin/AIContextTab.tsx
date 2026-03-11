import { useState, useEffect } from "react";
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

export function AIContextTab() {
  const { t } = useTranslation();
  const [facilitatorContent, setFacilitatorContent] = useState("");
  const [facilitatorLoading, setFacilitatorLoading] = useState(true);
  const [facilitatorSaving, setFacilitatorSaving] = useState(false);

  const [sectionsText, setSectionsText] = useState("");
  const [freeText, setFreeText] = useState("");
  const [companyLoading, setCompanyLoading] = useState(true);
  const [companySaving, setCompanySaving] = useState(false);

  useEffect(() => {
    fetchFacilitatorContext()
      .then((data) => setFacilitatorContent(data.content))
      .catch((err) => toast.error(`${t("admin.failedLoadFacilitator")}: ${err.message}`))
      .finally(() => setFacilitatorLoading(false));

    fetchCompanyContext()
      .then((data) => {
        setSectionsText(JSON.stringify(data.sections, null, 2));
        setFreeText(data.free_text);
      })
      .catch((err) => toast.error(`${t("admin.failedLoadCompany")}: ${err.message}`))
      .finally(() => setCompanyLoading(false));
  }, []);

  async function handleFacilitatorSave() {
    setFacilitatorSaving(true);
    try {
      await patchFacilitatorContext(facilitatorContent);
      toast.success(t("admin.facilitatorSaved"));
    } catch (err) {
      toast.error(`${t("admin.failedSaveFacilitator")}: ${(err as Error).message}`);
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
      await patchCompanyContext(sections, freeText);
      toast.success(t("admin.companySaved"));
    } catch (err) {
      toast.error(`${t("admin.failedSaveCompany")}: ${(err as Error).message}`);
    } finally {
      setCompanySaving(false);
    }
  }

  return (
    <div className="space-y-8 py-6">
      {/* Facilitator Context */}
      <section className="space-y-3">
        <h3 className="text-lg font-medium">{t("admin.facilitatorTitle")}</h3>
        {facilitatorLoading ? (
          <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
        ) : (
          <>
            <Textarea
              value={facilitatorContent}
              onChange={(e) => setFacilitatorContent(e.target.value)}
              rows={8}
              placeholder={t("admin.facilitatorPlaceholder")}
              data-testid="facilitator-textarea"
            />
            <Button onClick={handleFacilitatorSave} disabled={facilitatorSaving}>
              {facilitatorSaving ? t("common.saving") : t("admin.saveFacilitator")}
            </Button>
          </>
        )}
      </section>

      {/* Company Context */}
      <section className="space-y-3">
        <h3 className="text-lg font-medium">{t("admin.companyTitle")}</h3>
        {companyLoading ? (
          <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
        ) : (
          <>
            <div className="space-y-2">
              <label className="text-sm font-medium">{t("admin.sectionsJson")}</label>
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
              <label className="text-sm font-medium">{t("admin.freeText")}</label>
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
