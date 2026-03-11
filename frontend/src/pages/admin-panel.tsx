import { Navigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Brain, Settings, BarChart3, Users } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { AIContextTab } from "@/features/admin/AIContextTab";
import { ParametersTab } from "@/features/admin/ParametersTab";
import { MonitoringTab } from "@/features/admin/MonitoringTab";
import { UsersTab } from "@/features/admin/UsersTab";

export default function AdminPanel() {
  const { t } = useTranslation();
  const { hasRole } = useAuth();

  if (!hasRole("admin")) {
    return <Navigate to="/" replace />;
  }

  return (
      <div className="mx-auto w-full max-w-7xl px-4 py-6">
        <Tabs defaultValue="ai-context">
          <TabsList className="inline-flex h-auto w-full items-center justify-start gap-0 rounded-none border-b bg-transparent p-0">
            <TabsTrigger
              value="ai-context"
              className="inline-flex items-center gap-2 rounded-none border-b-2 border-transparent px-4 py-3 text-sm font-medium text-muted-foreground shadow-none transition-colors hover:bg-muted/50 hover:text-foreground data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none"
            >
              <Brain className="h-4 w-4" />
              {t("admin.aiContext")}
            </TabsTrigger>
            <TabsTrigger
              value="parameters"
              className="inline-flex items-center gap-2 rounded-none border-b-2 border-transparent px-4 py-3 text-sm font-medium text-muted-foreground shadow-none transition-colors hover:bg-muted/50 hover:text-foreground data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none"
            >
              <Settings className="h-4 w-4" />
              {t("admin.parameters")}
            </TabsTrigger>
            <TabsTrigger
              value="monitoring"
              className="inline-flex items-center gap-2 rounded-none border-b-2 border-transparent px-4 py-3 text-sm font-medium text-muted-foreground shadow-none transition-colors hover:bg-muted/50 hover:text-foreground data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none"
            >
              <BarChart3 className="h-4 w-4" />
              {t("admin.monitoring")}
            </TabsTrigger>
            <TabsTrigger
              value="users"
              className="inline-flex items-center gap-2 rounded-none border-b-2 border-transparent px-4 py-3 text-sm font-medium text-muted-foreground shadow-none transition-colors hover:bg-muted/50 hover:text-foreground data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none"
            >
              <Users className="h-4 w-4" />
              {t("admin.users")}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="ai-context">
            <AIContextTab />
          </TabsContent>
          <TabsContent value="parameters">
            <ParametersTab />
          </TabsContent>
          <TabsContent value="monitoring">
            <MonitoringTab />
          </TabsContent>
          <TabsContent value="users">
            <UsersTab />
          </TabsContent>
        </Tabs>
      </div>
  );
}
