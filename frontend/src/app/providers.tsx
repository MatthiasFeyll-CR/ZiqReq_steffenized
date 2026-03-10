import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Provider as ReduxProvider } from "react-redux";
import { createContext, createElement, useContext } from "react";
import { ToastContainer } from "react-toastify";
import { store } from "../store";
import { AuthContext } from "../hooks/use-auth";
import { useAuthProvider } from "../hooks/use-auth-provider";
import { useWebSocket } from "../hooks/use-websocket";
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
const WebSocketContext = createContext<SendMessageFn>(() => {});
export function useWsSend(): SendMessageFn {
  return useContext(WebSocketContext);
}

function AuthProvider({ children }: { children: ReactNode }) {
  const auth = useAuthProvider();
  return createElement(AuthContext.Provider, { value: auth }, children);
}

function WebSocketManager({ children }: { children: ReactNode }) {
  const { sendMessage } = useWebSocket();
  return (
    <WebSocketContext.Provider value={sendMessage}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function Providers({ children }: { children: ReactNode }) {
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
