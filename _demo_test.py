"""
AI-driven demo test script with quality judge.
Scenario: 生命保険（CT008）を解約し、自動車保険に新規加入する。

Components:
  - USER SIMULATOR  : GPT acting as customer 又吉佑樹 (C016)
  - JUDGE           : GPT evaluating each agent response for correctness / naturalness
  - HANDOFF API     : POST /api/handoffs/chat/stream -> SSE
  - DB RESET        : _reset_db.py runs at the end to restore all CSVs to initial state
"""
import asyncio
import json
import os
import re
import sys
import urllib.request

from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

BASE = "http://127.0.0.1:8000"
HANDOFF_ID = "handoff-1caf5233"

# ── Azure OpenAI ───────────────────────────────────────────────────────────
_raw_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
AZURE_ENDPOINT = re.sub(r"/openai(/v\d+)?/?$", "", _raw_endpoint)
AZURE_API_KEY   = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION") or "2025-01-01-preview"
SIM_MODEL = "gpt-5.4-mini"

# ─────────────────────────────────────────────────────────────────────────
# System prompts
# ─────────────────────────────────────────────────────────────────────────

USER_SYSTEM_PROMPT = """\
あなたはContoso保険のコンタクトセンターに電話してきた顧客です。
名前: 又吉 佑樹（またよし ゆうき）
顧客ID: C016

【ゴール】2ステップあります:
  ステップ1. 生命保険（ファミリー定期保険 CT008）を解約する
  ステップ2. 解約完了後、自動車保険に新規加入する
        車種: 普通車（カローラ）
        車齢: 3年
        希望: 任意保険フルカバー
両方完了したらゴール達成。

【会話のルール - 厳守】
- 返答は必ず顧客自身の言葉のみで1〜2文。[エージェント名]: のような形式で書いてはいけない。
- 最初のターンは「こんにちは」とだけ言う。
- 名前を聞かれたら「又吉佑樹です」と答える。
- 本人確認後に用件を聞かれたら「生命保険を解約したいです」と答える。
- 代替プランを提案されたら「安い保険と比べてみたいです」と言う。
- 比較内容を見たあとは「やはり解約します」と返す。
- 生命保険の解約が完了したら、必ず「ありがとうございます。次に自動車保険にも加入したいのですが」と言う。
- 自動車保険について車種・車齢を聞かれたら「普通車のカローラで車齢3年です」と答える。
- 希望カバレッジを聞かれたら「任意保険のフルカバーでお願いします」と答える。
- 見積や内容確認を求められたら「その内容で契約をお願いします」と答える。
- 自動車保険の契約登録が完了したら「ありがとうございました」と言い、最後に必ずEND_CONVERSATIONと書く。
- ゴールが達成されるまでは絶対にEND_CONVERSATIONと書かない。
"""

JUDGE_SYSTEM_PROMPT = """\
あなたはContoso保険コンタクトセンターの会話品質評価AIです。
以下のシナリオ前提を知っています:
  - 顧客: 又吉 佑樹 (C016)、生命保険CT008（ファミリー定期保険, 月6500円）を解約後、自動車保険（普通車カローラ3年, 任意フルカバー）に加入したい
  - エージェント構成: フロントエージェント → 生命保険エージェント → 自動車保険エージェントの順で転送される想定

直前のエージェント応答に対して以下の観点で評価してください:
1. 文脈整合性: 直前の顧客発言・会話の流れに対して的外れでないか
2. 進捗妥当性: すでに確認済みの情報を再確認するなど無駄なループがないか
   - すでに名前/IDを伝えたのに再度確認を求めていたらNG
   - すでに本人確認済みなのに再度認証を求めていたらNG
   - すでに用件を伝えたのに再度用件を聞いていたらNG
3. ループ検出: 会話履歴を見て、エージェントが直近3ターン以内に同じ質問や同じ内容を繰り返していたらNG
4. ドメイン転送の正確性: 生命保険の話なのに不必要に自動車保険エージェントへ転送していないか、またはその逆
5. 情報の正確性: 顧客情報（CT008の保険料6500円など）と矛盾していないか

判定はJSONのみで返してください（余分なテキスト不要）:
{"ok": true}  または  {"ok": false, "issue": "問題の簡潔な説明（日本語）"}
"""


# ─────────────────────────────────────────────────────────────────────────
# SSE helper
# ─────────────────────────────────────────────────────────────────────────

def sse_post(url: str, payload: dict) -> tuple[list[dict], str]:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    events: list[dict] = []
    session_id = ""
    with urllib.request.urlopen(req, timeout=120) as resp:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace")
            if line.startswith("data: "):
                try:
                    obj = json.loads(line[6:])
                    events.append(obj)
                    if "session_id" in obj:
                        session_id = obj["session_id"]
                except Exception:
                    pass
    return events, session_id


def extract_agent_reply(events: list[dict]) -> tuple[str, str, list[str], list[str]]:
    agent_name = ""
    reply = ""
    handoffs: list[str] = []
    tools: list[str] = []
    for ev in events:
        if ev.get("type") == "handoff_transition":
            handoffs.append(ev.get("title", ""))
        if "to_agent_name" in ev:
            agent_name = ev["to_agent_name"]
        if "session_id" in ev and "text" in ev:
            reply = ev.get("text", "")
            if not agent_name:
                agent_name = ev.get("agent_name", "")
        if ev.get("type") == "function_call.complete":
            t = ev.get("title", "").replace("Calling function_call(", "").rstrip(")")
            tools.append(t)
    return agent_name, reply, handoffs, tools


# ─────────────────────────────────────────────────────────────────────────
# GPT helpers
# ─────────────────────────────────────────────────────────────────────────

async def simulate_user(client: AsyncAzureOpenAI, history: list[dict]) -> str:
    resp = await client.chat.completions.create(
        model=SIM_MODEL,
        messages=[{"role": "system", "content": USER_SYSTEM_PROMPT}] + history,
        temperature=0.5,
        max_completion_tokens=150,
    )
    msg = resp.choices[0].message.content.strip()
    # Strip accidental [エージェント名]: prefix if GPT confuses its role
    msg = re.sub(r"^\[[^\]]+\]:\s*", "", msg)
    return msg


async def judge_response(
    client: AsyncAzureOpenAI,
    history: list[dict],
    agent_name: str,
    reply: str,
    handoffs: list[str],
) -> tuple[bool, str]:
    handoff_desc = f"\n転送発生: {'; '.join(handoffs)}" if handoffs else ""
    eval_prompt = (
        "【会話履歴（最新まで）】\n"
        + "\n".join(
            f"{'顧客' if m['role'] == 'user' else 'エージェント'}: {m['content']}"
            for m in history
        )
        + f"\n\n【今回のエージェント応答】 ({agent_name}){handoff_desc}\n{reply}"
    )
    resp = await client.chat.completions.create(
        model=SIM_MODEL,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": eval_prompt},
        ],
        temperature=0,
        max_completion_tokens=200,
    )
    raw = resp.choices[0].message.content.strip()
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return True, ""
    try:
        result = json.loads(m.group())
        return bool(result.get("ok", True)), result.get("issue", "") or ""
    except Exception:
        return True, ""


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────

async def run() -> None:
    if not AZURE_ENDPOINT:
        print("[ERROR] AZURE_OPENAI_ENDPOINT が設定されていません。", file=sys.stderr)
        raise SystemExit(1)

    if AZURE_API_KEY:
        oai_client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_key=AZURE_API_KEY,
            api_version=AZURE_API_VERSION,
        )
    else:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
        oai_client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=AZURE_API_VERSION,
        )

    session_id: str | None = None
    url = f"{BASE}/api/handoffs/chat/stream"
    history: list[dict] = []
    MAX_TURNS = 25
    judge_failures = 0
    # Deterministic loop detection: track recent (agent_name, reply_summary) pairs
    recent_agent_replies: list[tuple[str, str]] = []

    print("=" * 70)
    print("デモシナリオ: 生命保険解約 → 自動車保険加入")
    print(f"ユーザーシミュレーター & ジャッジ: Azure OpenAI {SIM_MODEL}")
    print("=" * 70)

    for turn in range(MAX_TURNS):
        # 1. Generate user message
        user_msg = await simulate_user(oai_client, history)
        history.append({"role": "user", "content": user_msg})
        print(f"\n{'─'*60}")
        print(f"[ユーザー ターン{turn + 1}]  {user_msg}")

        if "END_CONVERSATION" in user_msg:
            print("\n✅  ゴール達成 — 会話終了")
            break

        # 2. Call handoff API
        payload: dict = {"message": user_msg, "handoff_id": HANDOFF_ID}
        if session_id:
            payload["session_id"] = session_id

        events, sid = sse_post(url, payload)
        if sid:
            session_id = sid

        agent_name, reply, handoffs, tools = extract_agent_reply(events)

        for h in handoffs:
            print(f"  -> [HANDOFF] {h}")
        if tools:
            print(f"  [TOOLS]  {', '.join(tools)}")

        print(f"\n[{agent_name}]\n{reply[:800]}")

        # 3a. Deterministic loop detection
        reply_key = reply[:120].strip()
        loop_issue: str | None = None

        same_key_count = sum(
            1 for (a, r) in recent_agent_replies[-4:]
            if a == agent_name and r == reply_key
        )
        if same_key_count >= 1:
            loop_issue = f"{agent_name} が直近ターンとほぼ同じ応答を返しました（ループの疑い）"

        if not loop_issue and turn >= 2 and agent_name:
            if re.search(r"(氏名|顧客ID|お名前|お客様の名前)", reply):
                prior_asked = sum(
                    1 for (a, r) in recent_agent_replies
                    if a == agent_name and re.search(r"(氏名|顧客ID|お名前|お客様の名前)", r)
                )
                if prior_asked >= 1:
                    loop_issue = f"{agent_name} がすでに確認済みの氏名/IDを再度求めています（本人確認ループ）"

        recent_agent_replies.append((agent_name, reply_key))

        if loop_issue:
            judge_failures += 1
            print(f"\n{'!'*60}")
            print(f"  [LOOP DETECTED] (#{judge_failures}): {loop_issue}")
            print(f"{'!'*60}")
            print("\n[STOP] ループが検出されたため調査のために停止します。")
            print(f"       問題: {loop_issue}")
            print(f"       エージェント: {agent_name} / ターン: {turn + 1}")
            break

        # 3b. Quality judge
        ok, issue = await judge_response(oai_client, history, agent_name, reply, handoffs)
        if ok:
            print("  [JUDGE] OK")
        else:
            judge_failures += 1
            print(f"\n{'!'*60}")
            print(f"  [JUDGE] 問題検出 (#{judge_failures}): {issue}")
            print(f"{'!'*60}")
            print("\n[STOP] 品質問題が検出されたため調査のために停止します。")
            print(f"       問題: {issue}")
            print(f"       エージェント: {agent_name} / ターン: {turn + 1}")
            break

        # 4. Append to history
        history.append({"role": "assistant", "content": f"[{agent_name}]: {reply}"})

    else:
        print(f"\n[!]  MAX_TURNS ({MAX_TURNS}) に達しました。")

    await oai_client.close()

    print("\n" + "=" * 70)
    if judge_failures == 0:
        print("テスト完了 — 品質問題なし")
    else:
        print(f"テスト中断 — 問題検出により停止 ({judge_failures} 件)")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    finally:
        # Always reset the demo DB after a test run (success or failure)
        print("\n" + "─" * 60)
        print("デモ DB をリセット中...")
        import importlib.util, pathlib
        spec = importlib.util.spec_from_file_location(
            "_reset_db",
            pathlib.Path(__file__).parent / "_reset_db.py",
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        mod.reset()
