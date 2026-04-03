# MAF Workflow Studio

DevUI を参考にした **Microsoft Agent Framework 向けのローカル Web スタジオ**です。以下を 1 つの UI で行えます。

- エージェントの作成: `model` / `instructions` / `MCP` / `Agent Skills`
- Agent Skills の取込: **フォルダ upload** または **ファイル upload**
- ファイルベース Skill の Python スクリプトを **ローカル subprocess** で実行
- ワークフローの構築とテスト
- Edge 種別: `direct`, `conditional`, `switch-case`, `multi-selection`, `fan-in`
- Agent Framework の `WorkflowBuilder` コードプレビュー表示

---

## 1. セットアップ

```powershell
cd c:\Users\ymatayoshi\dev\20260331_maf_webui
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

必要なら `.env.example` を `.env` にコピーして値を設定します。

---

## 2. 起動

```powershell
cd c:\Users\ymatayoshi\dev\20260331_maf_webui
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

ブラウザーで `http://127.0.0.1:8000` を開きます。

---

## 3. モデル接続

### Mock preview
何も設定しなくても UI と workflow テストは動きます。

### OpenAI Responses
- `OPENAI_API_KEY`

### Azure OpenAI
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- 任意で `AZURE_OPENAI_API_VERSION`

### Azure AI Foundry
- `AZURE_AI_PROJECT_ENDPOINT`
- Azure 認証 (`az login` または `DefaultAzureCredential` が使える状態)

---

## 4. Skill の取り込み

- **フォルダ upload**: `SKILL.md`, `references/`, `scripts/` を含む skill フォルダをそのまま取り込み
- **ファイル upload**: 単体ファイル群をまとめて skill として登録
- スクリプト実行: 右ペインの **Run selected skill script** から JSON 引数付きでローカル subprocess 実行

サンプルとして `data/skills/unit-converter` を同梱しています。

---

## 5. Workflow Builder

1. 保存済み Agent をノードとして追加
2. Edge を選択して routing を定義
3. `Save workflow` または `Test workflow`
4. 下部に実行トレースと `WorkflowBuilder` コードプレビューを表示

条件 DSL の例:

- `contains:approve`
- `not_contains:spam`
- `regex:approve|ship`
- `default`

---

## 6. 参考

- DevUI: <https://github.com/microsoft/agent-framework/tree/main/python/packages/devui>
- File-based skills: <https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/skills/file_based_skill>
- Subprocess runner: <https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/skills/subprocess_script_runner.py>
- Agent skills docs: <https://learn.microsoft.com/ja-jp/agent-framework/agents/skills?pivots=programming-language-python>
- Hosted MCP tools docs: <https://learn.microsoft.com/ja-jp/agent-framework/agents/tools/hosted-mcp-tools?pivots=programming-language-python>
- Workflow edges docs: <https://learn.microsoft.com/ja-jp/agent-framework/workflows/edges?pivots=programming-language-python>
