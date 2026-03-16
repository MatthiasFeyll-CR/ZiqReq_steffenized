# Vision & Scope

## Product Vision

ZiqReq is an AI-assisted requirements assembly platform for Commerz Real that enables employees in specialized departments to create structured Requirements Documents for workflow improvement initiatives — without technical knowledge, bureaucratic overhead, or formal meetings. The AI helps non-technical users structure their requirements into hierarchical documents (Epics/User Stories for Software projects, Milestones/Work Packages for Non-Software projects), pre-loaded with Commerz Real's business context (systems, workflows, terminology), and automatically produces a review-ready Requirements Document that flows directly to the strategic software department.

## Target Audience

- **Primary:** Non-technical employees in specialized departments at Commerz Real who see opportunities to improve their workflows but lack the formal process or technical vocabulary to propose them.
- **Secondary:** The strategic software department (Reviewers) who receive, evaluate, and act on the submitted Requirements Documents.

## Problem Statement

Employees across Commerz Real's specialized departments regularly identify opportunities to improve their workflows. Today, turning those ideas into actionable requirements involves a high bureaucratic workload — formal proposal processes, multiple meetings, and manual document drafting. This creates a high inhibition threshold: many ideas are never proposed because the effort feels disproportionate.

Existing tools (Microsoft Whiteboard + Copilot, Miro, Notion AI) do not solve this because:

1. They provide generic AI assistance with no knowledge of Commerz Real's business context, existing systems, or domain terminology.
2. They require manual document creation after initial work — the gap between "rough draft" and "formal Requirements Document" remains.
3. They do not connect to a review/approval workflow — ideas still need to be manually routed to the right people.

ZiqReq closes the entire loop: structure requirements with context-aware AI → auto-generate Requirements Document → submit directly to reviewers.

## Scale & Context

- **Expected users:** ~2,000 employees (long-term target, potentially more)
- **Expected project volume:** Up to ~10,000 projects/month at peak adoption, tapering to a steady state over time
- **Adoption pattern:** High initial peak as employees explore the tool, settling to a lower sustained rate
- **Deployment:** Internal, single-tenant
- **Access model:** Private — Commerz Real employees only, authenticated via Microsoft Azure AD

## Non-Goals (Out of Scope)

1. **No project management.** ZiqReq does not manage project execution after a Requirements Document is accepted. No task boards, sprints, timelines, or implementation tracking.
2. **No meeting replacement mandate.** ZiqReq is an alternative low-friction channel for capturing and structuring requirements, not a policy to eliminate face-to-face collaboration.
3. **No technical details in output.** The Requirements Document stays at the business requirements level. Users have no technical software engineering background — the system does not produce architecture, data models, or implementation specifications.
4. **No external users.** The platform is exclusively for Commerz Real employees. No external access under any circumstances.
5. **Not a general-purpose AI chat tool.** The AI is scoped specifically to structuring business requirements within Commerz Real's context. It is not a knowledge base, search engine, or open-ended assistant.
