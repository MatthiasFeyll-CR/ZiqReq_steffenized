import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useCreateIdea } from "@/hooks/use-create-idea";

export function HeroSection() {
  const { t } = useTranslation();
  const [value, setValue] = useState("");
  const [validationError, setValidationError] = useState("");
  const mutation = useCreateIdea();

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed) {
      setValidationError(t("landing.hero.validationEmpty"));
      return;
    }
    setValidationError("");
    mutation.mutate(trimmed);
  };

  return (
    <section className="flex flex-col items-center gap-4 py-16 text-center">
      <h1 className="text-3xl font-bold text-foreground">
        {t("landing.hero.heading")}
      </h1>
      <p className="max-w-md text-text-secondary">
        {t("landing.hero.subtext")}
      </p>
      <div className="mt-4 flex w-full max-w-lg flex-col gap-2">
        <Textarea
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            if (validationError) setValidationError("");
            if (mutation.isError) mutation.reset();
          }}
          placeholder={t("landing.hero.placeholder")}
          className="min-h-24 resize-none"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
        />
        {validationError && (
          <p className="text-sm text-destructive" role="alert">
            {validationError}
          </p>
        )}
        {mutation.isError && (
          <div
            className="flex items-center justify-between rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100"
            role="alert"
          >
            <span>{t("landing.hero.errorCreating")}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => mutation.mutate(value.trim())}
            >
              {t("common.retry")}
            </Button>
          </div>
        )}
        <Button
          variant="primary"
          size="lg"
          className="self-end"
          onClick={handleSubmit}
          disabled={mutation.isPending}
        >
          {mutation.isPending && (
            <Loader2 className="mr-2 h-4 w-4 motion-safe:animate-spin" />
          )}
          {t("landing.hero.submit")}
        </Button>
      </div>
    </section>
  );
}
