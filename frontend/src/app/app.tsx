import { Providers } from "./providers";
import { AppRouter } from "./router";
import { SkipLink } from "@/components/common/SkipLink";
import "./globals.css";

export function App() {
  return (
    <Providers>
      <SkipLink />
      <AppRouter />
    </Providers>
  );
}
