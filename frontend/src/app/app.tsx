import { Providers } from "./providers";
import { AppRouter } from "./router";
import "./globals.css";

export function App() {
  return (
    <Providers>
      <AppRouter />
    </Providers>
  );
}
