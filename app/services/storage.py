from __future__ import annotations

import json
from pathlib import Path

from app.core.config import AGENTS_DIR, HANDOFFS_DIR, STATE_FILE
from app.models import AgentConfig, HandoffDefinition, MCPToolConfig, ModelSettings, NodePosition, StudioState, WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.services.skill_runner import discover_skills


class StudioRepository:
    def __init__(self, state_file: Path = STATE_FILE) -> None:
        self.state_file = state_file

    def _default_state(self) -> StudioState:
        planner = AgentConfig(
            id="agent-planner",
            name="Planner Agent",
            description="Plans how to execute the request and proposes a first draft.",
            instructions=(
                "You are a planning agent inside a workflow studio. Break the user request into actionable steps, "
                "call skills when useful, and produce concise structured output."
            ),
            model=ModelSettings(provider="mock", model="gpt-4.1-mini"),
            skill_ids=["unit-converter"],
            default_prompt="Create a 3-step implementation plan for the requested task.",
        )
        reviewer = AgentConfig(
            id="agent-reviewer",
            name="Reviewer Agent",
            description="Validates the planner output and suggests improvements.",
            instructions="You are a reviewer agent. Critique the plan, highlight risks, and produce a final recommendation.",
            model=ModelSettings(provider="mock", model="gpt-4.1-mini"),
            mcp_tools=[
                MCPToolConfig(
                    name="Microsoft Learn MCP",
                    url="https://learn.microsoft.com/api/mcp",
                    approval_mode="never_require",
                    description="Search Microsoft Learn content.",
                )
            ],
            default_prompt="Review the implementation plan and call out any missing details.",
        )
        workflow = WorkflowDefinition(
            id="wf-demo",
            name="Planner to Reviewer",
            description="Starter workflow that chains a planning agent into a reviewer.",
            input_text="Build a MAF workflow and summarize the output.",
            start_node_id="node-planner",
            nodes=[
                WorkflowNode(id="node-planner", title="Planner", agent_id=planner.id, position=NodePosition(x=80, y=80)),
                WorkflowNode(id="node-reviewer", title="Reviewer", agent_id=reviewer.id, position=NodePosition(x=420, y=200)),
            ],
            edges=[
                WorkflowEdge(id="edge-demo", source="node-planner", target="node-reviewer", edge_type="direct", label="plan → review")
            ],
        )
        return StudioState(agents=[planner, reviewer], workflows=[workflow], skills=discover_skills())

    # ── Individual file helpers ───────────────────────────────────

    def _load_agents(self) -> list[AgentConfig]:
        agents = []
        for f in sorted(AGENTS_DIR.glob("*.json")):
            try:
                agents.append(AgentConfig(**json.loads(f.read_text(encoding="utf-8"))))
            except Exception:
                pass
        return sorted(agents, key=lambda a: a.name.lower())

    def _load_handoffs(self) -> list[HandoffDefinition]:
        handoffs = []
        for f in sorted(HANDOFFS_DIR.glob("*.json")):
            try:
                handoffs.append(HandoffDefinition(**json.loads(f.read_text(encoding="utf-8"))))
            except Exception:
                pass
        return sorted(handoffs, key=lambda h: h.name.lower())

    def _save_agent_file(self, agent: AgentConfig) -> None:
        (AGENTS_DIR / f"{agent.id}.json").write_text(
            json.dumps(agent.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def _save_handoff_file(self, handoff: HandoffDefinition) -> None:
        (HANDOFFS_DIR / f"{handoff.id}.json").write_text(
            json.dumps(handoff.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def _delete_agent_file(self, agent_id: str) -> None:
        (AGENTS_DIR / f"{agent_id}.json").unlink(missing_ok=True)

    def _delete_handoff_file(self, handoff_id: str) -> None:
        (HANDOFFS_DIR / f"{handoff_id}.json").unlink(missing_ok=True)

    def _load_workflows(self) -> list[WorkflowDefinition]:
        if not self.state_file.exists():
            return []
        payload = json.loads(self.state_file.read_text(encoding="utf-8"))
        return [WorkflowDefinition(**w) for w in payload.get("workflows", [])]

    def _save_workflows(self, workflows: list[WorkflowDefinition]) -> None:
        payload = {"workflows": [w.model_dump(mode="json") for w in workflows]}
        self.state_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _migrate_legacy(self) -> None:
        """studio_state.json にある agents/handoffs を個別ファイルへ移行（初回のみ）。"""
        if not self.state_file.exists():
            return
        payload = json.loads(self.state_file.read_text(encoding="utf-8"))
        migrated = False
        for agent_data in payload.get("agents", []):
            dest = AGENTS_DIR / f"{agent_data['id']}.json"
            if not dest.exists():
                agent = AgentConfig(**agent_data)
                dest.write_text(json.dumps(agent.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8")
                migrated = True
        for handoff_data in payload.get("handoffs", []):
            dest = HANDOFFS_DIR / f"{handoff_data['id']}.json"
            if not dest.exists():
                handoff = HandoffDefinition(**handoff_data)
                dest.write_text(json.dumps(handoff.model_dump(mode="json"), indent=2, ensure_ascii=False), encoding="utf-8")
                migrated = True
        if migrated or "agents" in payload or "handoffs" in payload:
            # agents/handoffs を除いた状態で state_file を上書き
            self._save_workflows([WorkflowDefinition(**w) for w in payload.get("workflows", [])])

    # ── Public API ────────────────────────────────────────────────

    def load_state(self) -> StudioState:
        self._migrate_legacy()
        agents = self._load_agents()
        handoffs = self._load_handoffs()
        workflows = self._load_workflows()

        if not agents and not workflows:
            state = self._default_state()
            self.save_state(state)
            return state

        state = StudioState(agents=agents, workflows=workflows, handoffs=handoffs, skills=discover_skills())
        return state

    def save_state(self, state: StudioState) -> None:
        for agent in state.agents:
            self._save_agent_file(agent)
        for handoff in state.handoffs:
            self._save_handoff_file(handoff)
        self._save_workflows(state.workflows)

    def upsert_agent(self, agent: AgentConfig) -> StudioState:
        self._save_agent_file(agent)
        return self.load_state()

    def upsert_workflow(self, workflow: WorkflowDefinition) -> StudioState:
        workflows = self._load_workflows()
        updated = [w for w in workflows if w.id != workflow.id]
        updated.append(workflow)
        self._save_workflows(sorted(updated, key=lambda w: w.name.lower()))
        return self.load_state()

    def delete_agent(self, agent_id: str) -> StudioState:
        self._delete_agent_file(agent_id)
        return self.load_state()

    def upsert_handoff(self, handoff: HandoffDefinition) -> StudioState:
        self._save_handoff_file(handoff)
        return self.load_state()

    def delete_handoff(self, handoff_id: str) -> StudioState:
        self._delete_handoff_file(handoff_id)
        return self.load_state()

    def get_handoff(self, handoff_id: str) -> HandoffDefinition | None:
        p = HANDOFFS_DIR / f"{handoff_id}.json"
        if p.exists():
            return HandoffDefinition(**json.loads(p.read_text(encoding="utf-8")))
        return None

    def get_agent(self, agent_id: str) -> AgentConfig | None:
        p = AGENTS_DIR / f"{agent_id}.json"
        if p.exists():
            return AgentConfig(**json.loads(p.read_text(encoding="utf-8")))
        return None

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        return next((w for w in self._load_workflows() if w.id == workflow_id), None)
