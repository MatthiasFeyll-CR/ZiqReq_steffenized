import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Clipboard, GitMerge, Loader2, Search } from "lucide-react";
import { toast } from "react-toastify";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getSimilarIdeas,
  createManualMergeRequest,
  type SimilarIdea,
} from "@/api/similarity";

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const URL_UUID_REGEX = /\/idea\/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\/?/i;

function extractUuidFromInput(input: string): { uuid?: string; url?: string } | null {
  const trimmed = input.trim();
  if (!trimmed) return null;

  if (UUID_REGEX.test(trimmed)) {
    return { uuid: trimmed };
  }

  const match = trimmed.match(URL_UUID_REGEX);
  if (match) {
    return { url: trimmed };
  }

  return null;
}

interface ManualMergeModalProps {
  ideaId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function ManualMergeModal({
  ideaId,
  open,
  onOpenChange,
  onSuccess,
}: ManualMergeModalProps) {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const parsed = extractUuidFromInput(inputValue);
  const isValidInput = parsed !== null;

  const {
    data: similarData,
    isLoading: similarLoading,
  } = useQuery({
    queryKey: ["similar-ideas", ideaId],
    queryFn: () => getSimilarIdeas(ideaId),
    enabled: open,
  });

  async function handlePaste() {
    try {
      const text = await navigator.clipboard.readText();
      setInputValue(text);
      setError(null);
    } catch {
      // Clipboard API may not be available
    }
  }

  async function handleSubmitUuid() {
    if (!parsed) {
      setError(t("merge.invalidUuid"));
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const target = parsed.url
        ? { target_idea_url: parsed.url }
        : { target_idea_id: parsed.uuid };
      await createManualMergeRequest(ideaId, target);
      toast.success(t("merge.mergeRequestSent"));
      setInputValue("");
      onOpenChange(false);
      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : t("merge.failedToCreate");
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRequestMerge(targetId: string) {
    setSubmitting(true);
    setError(null);
    try {
      await createManualMergeRequest(ideaId, { target_idea_id: targetId });
      toast.success(t("merge.mergeRequestSent"));
      onOpenChange(false);
      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : t("merge.failedToCreate");
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) {
          setInputValue("");
          setError(null);
        }
        onOpenChange(v);
      }}
    >
      <DialogContent className="max-w-lg" data-testid="manual-merge-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GitMerge className="h-5 w-5" />
            {t("merge.requestTitle")}
          </DialogTitle>
          <DialogDescription>
            {t("merge.requestDescription")}
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="uuid" className="mt-2">
          <TabsList className="w-full">
            <TabsTrigger value="uuid" className="flex-1" data-testid="tab-uuid">
              {t("merge.tabUuid")}
            </TabsTrigger>
            <TabsTrigger value="browse" className="flex-1" data-testid="tab-browse">
              {t("merge.tabBrowse")}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="uuid" data-testid="tab-content-uuid">
            <div className="flex flex-col gap-3 py-2">
              <div className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => {
                    setInputValue(e.target.value);
                    setError(null);
                  }}
                  placeholder={t("merge.uuidPlaceholder")}
                  data-testid="uuid-input"
                  className="flex-1"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handlePaste}
                  aria-label="Paste from clipboard"
                  data-testid="paste-button"
                >
                  <Clipboard className="h-4 w-4" />
                </Button>
              </div>

              {inputValue && !isValidInput && (
                <p className="text-sm text-destructive" data-testid="validation-error">
                  {t("merge.invalidUuidUrl")}
                </p>
              )}

              {error && (
                <p className="text-sm text-destructive" data-testid="submit-error">
                  {error}
                </p>
              )}

              <Button
                variant="primary"
                onClick={handleSubmitUuid}
                disabled={!isValidInput || submitting}
                data-testid="submit-uuid-button"
              >
                {submitting && <Loader2 className="mr-1 h-4 w-4 motion-safe:animate-spin" />}
                {t("merge.requestMerge")}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="browse" data-testid="tab-content-browse">
            <div className="flex flex-col gap-2 py-2 max-h-80 overflow-y-auto">
              {similarLoading && (
                <div className="flex flex-col gap-2" data-testid="similar-loading">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              )}

              {!similarLoading && (!similarData || similarData.results.length === 0) && (
                <div className="flex flex-col items-center gap-2 py-8 text-muted-foreground" data-testid="similar-empty">
                  <Search className="h-8 w-8" />
                  <p className="text-sm">{t("merge.noSimilar")}</p>
                </div>
              )}

              {!similarLoading && similarData?.results.map((idea: SimilarIdea) => (
                <SimilarIdeaRow
                  key={idea.id}
                  idea={idea}
                  onRequestMerge={() => handleRequestMerge(idea.id)}
                  disabled={submitting}
                />
              ))}

              {error && (
                <p className="text-sm text-destructive" data-testid="browse-error">
                  {error}
                </p>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

function SimilarIdeaRow({
  idea,
  onRequestMerge,
  disabled,
}: {
  idea: SimilarIdea;
  onRequestMerge: () => void;
  disabled: boolean;
}) {
  const { t } = useTranslation();
  return (
    <div
      className="flex items-center justify-between gap-3 rounded-md border p-3"
      data-testid={`similar-idea-${idea.id}`}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium truncate">{idea.title}</p>
          {idea.similarity_type === "declined_merge" && (
            <span
              className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
              data-testid="declined-badge"
            >
              {t("merge.previouslyDeclined")}
            </span>
          )}
        </div>
        {idea.keywords.length > 0 && (
          <p className="text-xs text-muted-foreground truncate mt-0.5">
            {idea.keywords.join(", ")}
          </p>
        )}
      </div>
      <Button
        variant="outline"
        size="sm"
        onClick={onRequestMerge}
        disabled={disabled}
        data-testid={`merge-button-${idea.id}`}
      >
        <GitMerge className="mr-1 h-3 w-3" />
        {t("merge.requestMerge")}
      </Button>
    </div>
  );
}
