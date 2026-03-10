import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  pushAction,
  undo,
  redo,
  selectCanUndo,
  selectCanRedo,
  selectUndoTop,
  selectRedoTop,
  type UndoEntry,
} from "@/store/board-slice";
import { updateBoardNode } from "@/api/board";
import type { AppDispatch } from "@/store/index";

export function useBoardUndo(ideaId: string | undefined) {
  const dispatch = useDispatch<AppDispatch>();
  const canUndo = useSelector(selectCanUndo);
  const canRedo = useSelector(selectCanRedo);
  const undoTop = useSelector(selectUndoTop);
  const redoTop = useSelector(selectRedoTop);

  const push = useCallback(
    (entry: UndoEntry) => {
      dispatch(pushAction(entry));
    },
    [dispatch],
  );

  const handleUndo = useCallback(() => {
    if (!undoTop) return;
    const { nodeId, previousState } = undoTop;
    dispatch(undo());
    if (ideaId) {
      updateBoardNode(ideaId, nodeId, previousState).catch(() => {
        // Will be retried on next sync
      });
    }
  }, [dispatch, ideaId, undoTop]);

  const handleRedo = useCallback(() => {
    if (!redoTop) return;
    const { nodeId, data } = redoTop;
    dispatch(redo());
    if (ideaId) {
      updateBoardNode(ideaId, nodeId, data).catch(() => {
        // Will be retried on next sync
      });
    }
  }, [dispatch, ideaId, redoTop]);

  return {
    push,
    handleUndo,
    handleRedo,
    canUndo,
    canRedo,
    undoTop,
    redoTop,
  };
}
