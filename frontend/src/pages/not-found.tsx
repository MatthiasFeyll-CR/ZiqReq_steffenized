import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div
      className="flex flex-col items-center justify-center h-full gap-6 py-24 px-4"
      data-testid="not-found-page"
    >
      <span className="text-8xl font-bold text-muted-foreground/30">404</span>
      <h1 className="text-2xl font-semibold text-foreground">
        {t("notFound.title", "Page not found")}
      </h1>
      <p className="text-sm text-muted-foreground text-center max-w-md">
        {t("notFound.description", "The page you're looking for doesn't exist or has been moved.")}
      </p>
      <Button variant="outline" onClick={() => navigate("/")}>
        {t("notFound.backHome", "Back to Home")}
      </Button>
    </div>
  );
}
