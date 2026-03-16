interface WorkspaceLayoutProps {
  chatPanel?: React.ReactNode;
}

export function WorkspaceLayout({ chatPanel }: WorkspaceLayoutProps) {
  return (
    <div
      className="flex flex-1 overflow-hidden"
      data-testid="workspace-layout"
    >
      <div
        className="flex flex-col h-full w-full overflow-hidden"
        data-testid="chat-panel"
      >
        {chatPanel ?? (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            Chat
          </div>
        )}
      </div>
    </div>
  );
}
