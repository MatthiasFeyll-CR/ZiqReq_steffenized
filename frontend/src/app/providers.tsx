import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Provider as ReduxProvider } from "react-redux";
import { MsalProvider } from "@azure/msal-react";
import { createContext, createElement, useContext } from "react";
import { ToastContainer } from "react-toastify";
import { store } from "../store";
import { AuthContext } from "../hooks/use-auth";
import { useAuthProvider } from "../hooks/use-auth-provider";
import { useWebSocket } from "../hooks/use-websocket";
import { msalInstance } from "../config/msalConfig";
import { env } from "../config/env";
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

type SendMessageFn = (msg: Record<string, unknown>) => void;
type ReconnectFn = () => void;
const WebSocketContext = createContext<SendMessageFn>(() => {});
const ReconnectContext = createContext<ReconnectFn>(() => {});
export function useWsSend(): SendMessageFn {
  return useContext(WebSocketContext);
}
export function useWsReconnect(): ReconnectFn {
  return useContext(ReconnectContext);
}

function AuthProvider({ children }: { children: ReactNode }) {
  const auth = useAuthProvider();
  return createElement(AuthContext.Provider, { value: auth }, children);
}

function WebSocketManager({ children }: { children: ReactNode }) {
  const { sendMessage, reconnectNow } = useWebSocket();
  return (
    <WebSocketContext.Provider value={sendMessage}>
      <ReconnectContext.Provider value={reconnectNow}>
        {children}
      </ReconnectContext.Provider>
    </WebSocketContext.Provider>
  );
}

function AppProviders({ children }: { children: ReactNode }) {
  return (
    <ReduxProvider store={store}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <WebSocketManager>
            {children}
          </WebSocketManager>
          <ToastContainer position="bottom-right" />
        </AuthProvider>
      </QueryClientProvider>
    </ReduxProvider>
  );
}

export function Providers({ children }: { children: ReactNode }) {
  // In dev bypass mode, skip MsalProvider entirely
  if (env.authBypass) {
    return <AppProviders>{children}</AppProviders>;
  }

  return (
    <MsalProvider instance={msalInstance}>
      <AppProviders>{children}</AppProviders>
    </MsalProvider>
  );
}
