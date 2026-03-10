import { Plus, Trash2, Maximize2 } from "lucide-react";
import { useReactFlow } from "@xyflow/react";
import { Button } from "@/components/ui/button";

interface BoardToolbarProps {
  selectedCount: number;
  onAddBox: (position: { x: number; y: number }) => void;
  onDeleteSelected: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
  undoTopSource?: "user" | "ai";
  redoTopSource?: "user" | "ai";
}

export function BoardToolbar({
  selectedCount,
  onAddBox,
  onDeleteSelected,
}: BoardToolbarProps) {
  const { fitView, screenToFlowPosition } = useReactFlow();

  const handleAddBox = () => {
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    const position = screenToFlowPosition({ x: centerX, y: centerY });
    onAddBox(position);
  };

  const handleFitView = () => {
    fitView({ padding: 0.1 });
  };

  return (
    <div
      className="flex items-center border-b bg-card h-10 px-2 gap-1"
      data-testid="board-toolbar"
    >
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={handleAddBox}
        title="Add Box"
        data-testid="toolbar-add-box"
      >
        <Plus className="h-4 w-4" />
      </Button>

      <div className="w-px h-5 bg-border mx-1" />

      <Button
        variant="ghost"
        size="icon-sm"
        onClick={onDeleteSelected}
        disabled={selectedCount === 0}
        title="Delete Selected"
        data-testid="toolbar-delete"
      >
        <Trash2 className="h-4 w-4" />
      </Button>

      <div className="w-px h-5 bg-border mx-1" />

      <Button
        variant="ghost"
        size="icon-sm"
        onClick={handleFitView}
        title="Fit View"
        data-testid="toolbar-fit-view"
      >
        <Maximize2 className="h-4 w-4" />
      </Button>
    </div>
  );
}
