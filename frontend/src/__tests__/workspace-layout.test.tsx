import { describe, it, expect, beforeAll } from "vitest";
import { render, screen } from "@testing-library/react";
import i18n from "@/i18n/config";

import { WorkspaceLayout } from "@/components/workspace/WorkspaceLayout";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

describe("WorkspaceLayout", () => {
  it("renders chat panel full width", () => {
    render(<WorkspaceLayout chatPanel={<div>Chat Content</div>} />);

    expect(screen.getByTestId("workspace-layout")).toBeInTheDocument();
    expect(screen.getByTestId("chat-panel")).toBeInTheDocument();
    expect(screen.getByText("Chat Content")).toBeInTheDocument();
  });

  it("renders default chat placeholder when no chatPanel prop", () => {
    render(<WorkspaceLayout />);

    expect(screen.getByText("Chat")).toBeInTheDocument();
  });
});
