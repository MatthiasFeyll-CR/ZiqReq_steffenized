import { Navigate } from "react-router-dom";
import { Brain, Settings, BarChart3, Users } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { PageShell } from "@/components/layout/PageShell";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function AdminPanel() {
  const { hasRole } = useAuth();

  if (!hasRole("admin")) {
    return <Navigate to="/landing" replace />;
  }

  return (
    <PageShell>
      <div className="mx-auto w-full max-w-7xl px-4 py-6">
        <Tabs defaultValue="ai-context">
          <TabsList className="inline-flex h-auto w-full items-center justify-start gap-0 rounded-none border-b bg-transparent p-0">
            <TabsTrigger
              value="ai-context"
              className="inline-flex items-center gap-2 rounded-none border-b-2 border-transparent px-4 py-3 text-sm font-medium text-muted-foreground shadow-none transition-colors hover:bg-muted/50 hover:text-foreground data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none"
            >
              <Brain className="h-4 w-4" />
              AI Context
            </TabsTrigger>
            <TabsTrigger
              value="parameters"
              className="inline-flex items-center gap-2 rounded-none border-b-2 border-transparent px-4 py-3 text-sm font-medium text-muted-foreground shadow-none transition-colors hover:bg-muted/50 hover:text-foreground data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none"
            >
              <Settings className="h-4 w-4" />
              Parameters
            </TabsTrigger>
            <TabsTrigger
              value="monitoring"
              className="inline-flex items-center gap-2 rounded-none border-b-2 border-transparent px-4 py-3 text-sm font-medium text-muted-foreground shadow-none transition-colors hover:bg-muted/50 hover:text-foreground data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none"
            >
              <BarChart3 className="h-4 w-4" />
              Monitoring
            </TabsTrigger>
            <TabsTrigger
              value="users"
              className="inline-flex items-center gap-2 rounded-none border-b-2 border-transparent px-4 py-3 text-sm font-medium text-muted-foreground shadow-none transition-colors hover:bg-muted/50 hover:text-foreground data-[state=active]:border-primary data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none"
            >
              <Users className="h-4 w-4" />
              Users
            </TabsTrigger>
          </TabsList>

          <TabsContent value="ai-context">
            <div className="py-6">
              <p className="text-muted-foreground">AI Context management</p>
            </div>
          </TabsContent>
          <TabsContent value="parameters">
            <div className="py-6">
              <p className="text-muted-foreground">Parameters management</p>
            </div>
          </TabsContent>
          <TabsContent value="monitoring">
            <div className="py-6">
              <p className="text-muted-foreground">Monitoring dashboard</p>
            </div>
          </TabsContent>
          <TabsContent value="users">
            <div className="py-6">
              <p className="text-muted-foreground">User search</p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </PageShell>
  );
}
