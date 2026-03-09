import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Provider as ReduxProvider } from "react-redux";
import { createElement } from "react";
import { ToastContainer } from "react-toastify";
import { store } from "../store";
import { AuthContext } from "../hooks/use-auth";
import { useAuthProvider } from "../hooks/use-auth-provider";
import type { ReactNode } from "react";
import "../i18n/config";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      retry: 3,
    },
  },
});

function AuthProvider({ children }: { children: ReactNode }) {
  const auth = useAuthProvider();
  return createElement(AuthContext.Provider, { value: auth }, children);
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ReduxProvider store={store}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          {children}
          <ToastContainer position="bottom-right" />
        </AuthProvider>
      </QueryClientProvider>
    </ReduxProvider>
  );
}
