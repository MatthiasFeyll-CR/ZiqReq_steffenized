import { useState, useEffect } from "react";
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
      .catch((err) => toast.error(`Failed to load facilitator context: ${err.message}`))
      .finally(() => setFacilitatorLoading(false));

    fetchCompanyContext()
      .then((data) => {
        setSectionsText(JSON.stringify(data.sections, null, 2));
        setFreeText(data.free_text);
      })
      .catch((err) => toast.error(`Failed to load company context: ${err.message}`))
      .finally(() => setCompanyLoading(false));
  }, []);

  async function handleFacilitatorSave() {
    setFacilitatorSaving(true);
    try {
      await patchFacilitatorContext(facilitatorContent);
      toast.success("Facilitator context saved");
    } catch (err) {
      toast.error(`Failed to save facilitator context: ${(err as Error).message}`);
    } finally {
      setFacilitatorSaving(false);
    }
  }

  async function handleCompanySave() {
    let sections: Record<string, unknown>;
    try {
      sections = JSON.parse(sectionsText);
    } catch {
      toast.error("Sections must be valid JSON");
      return;
    }
    setCompanySaving(true);
    try {
      await patchCompanyContext(sections, freeText);
      toast.success("Company context saved");
    } catch (err) {
      toast.error(`Failed to save company context: ${(err as Error).message}`);
    } finally {
      setCompanySaving(false);
    }
  }

  return (
    <div className="space-y-8 py-6">
      {/* Facilitator Context */}
      <section className="space-y-3">
        <h3 className="text-lg font-medium">Facilitator Context (Table of Contents)</h3>
        {facilitatorLoading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : (
          <>
            <Textarea
              value={facilitatorContent}
              onChange={(e) => setFacilitatorContent(e.target.value)}
              rows={8}
              placeholder="Enter facilitator context..."
              data-testid="facilitator-textarea"
            />
            <Button onClick={handleFacilitatorSave} disabled={facilitatorSaving}>
              {facilitatorSaving ? "Saving..." : "Save Facilitator Context"}
            </Button>
          </>
        )}
      </section>

      {/* Company Context */}
      <section className="space-y-3">
        <h3 className="text-lg font-medium">Company Context (Detailed)</h3>
        {companyLoading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : (
          <>
            <div className="space-y-2">
              <label className="text-sm font-medium">Sections (JSON)</label>
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
              <label className="text-sm font-medium">Free Text</label>
              <Textarea
                value={freeText}
                onChange={(e) => setFreeText(e.target.value)}
                rows={6}
                placeholder="Additional unstructured content..."
                data-testid="freetext-textarea"
              />
            </div>
            <Button onClick={handleCompanySave} disabled={companySaving}>
              {companySaving ? "Saving..." : "Save Company Context"}
            </Button>
          </>
        )}
      </section>
    </div>
  );
}
