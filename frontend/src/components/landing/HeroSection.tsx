import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface HeroSectionProps {
  onSubmit?: (message: string) => void;
}

export function HeroSection({ onSubmit }: HeroSectionProps) {
  const { t } = useTranslation();
  const [value, setValue] = useState("");

  const handleSubmit = () => {
    if (value.trim() && onSubmit) {
      onSubmit(value.trim());
    }
  };

  return (
    <section className="flex flex-col items-center gap-4 py-16 text-center">
      <h1 className="text-3xl font-bold text-foreground">
        {t("landing.hero.heading")}
      </h1>
      <p className="max-w-md text-text-secondary">
        {t("landing.hero.subtext")}
      </p>
      <div className="mt-4 flex w-full max-w-lg gap-2">
        <Input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={t("landing.hero.placeholder")}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSubmit();
          }}
        />
        <Button variant="primary" onClick={handleSubmit}>
          {t("landing.hero.submit")}
        </Button>
      </div>
    </section>
  );
}
