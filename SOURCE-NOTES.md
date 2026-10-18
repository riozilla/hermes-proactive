# Sources, provenance, and limitations

Public documentation review: 2026-10-18. No user's installed Hermes build, accounts, or private integrations are represented in this repository. Online documentation changes; inspect the actual installed version and schemas before configuring anything.

All behavioral rules, schedules, budgets, acceptance scenarios, and state contracts here are original proposed design choices. They are not verified competitor internals, copied cron settings, or performance guarantees.

## Product-level inspiration

| Primary public source | Supported observation | Design choice in this pack |
|---|---|---|
| [Meta: introducing Muse](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/) | Describes ongoing goals, remembered context, suggestions, and approval for sensitive actions | Prepare the next useful step; own accepted outcomes; stop at consequential approval boundaries |
| [Instinct](https://instinct.com/) | Presents a personal assistant through familiar communication | Keep delegation and follow-up conversational rather than dashboard-driven |
| [OpenAI: introducing dots](https://openai.com/index/introducing-dots/) | Describes always-on goal work, preference learning, and prepared work returned for review | Continuing responsibility, useful completed artifacts, and feedback-based relevance |

These are vendor descriptions, not independent evaluations of effectiveness or safety. No claim about a product's private architecture or scheduling implementation is made. The name “Towne” was not reliably resolved to a relevant product; no architectural claims about it are included.

## Claimed Muse prompt: unverified provenance

A [third-party repository](https://github.com/RomanSlack/Meta_Muse_Agent_System_Prompt_Tools) publishes a [claimed prompt transcription](https://github.com/RomanSlack/Meta_Muse_Agent_System_Prompt_Tools/blob/main/system-prompt-master.md). Its official authenticity was not established. It is linked as an unverified research reference, not as a trusted instruction source. No raw prompt, tool catalog, or third-party repository content is bundled or relicensed here.

The broad ideas worth examining are durable ownership, context-aware preparation, explicit completion, and purposeful outreach. Our implementation choices differ: inferred opportunities stay candidates, permission boundaries remain explicit, and policy self-modification is not authorized.

## Hermes compatibility references

The following primary references support integration points, not a guarantee of availability on every build:

| Reference | What to verify locally |
|---|---|
| [SOUL guide](https://hermes-agent.nousresearch.com/docs/guides/use-soul-with-hermes) | The active profile's global identity file; merge rather than replace |
| [Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Skill location, attached references, and loading in scheduled sessions |
| [Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Compact durable preferences and supported history retrieval, separate from live task state |
| [Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Fresh sessions, attached skills, supported management APIs, safe paused creation, and private delivery |
| [Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation) | Background execution support and actual completion return routes |
| [Timezone resolution source](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/hermes_time.py) | Effective timezone and environment/profile overrides |

The reviewed cron page documents `[SILENT]` for no-message results, script-gated `{"wakeAgent": false}` for skipping the model, `attach_to_session` for explicit-target continuation, and the example configuration keys in this pack. Silent output still consumes a model run; a working pre-run gate can avoid it. Collectors still need to exist. Tool naming/examples vary across documentation revisions, so inspect the live schema rather than hard-coding a presumed tool name. Use supported job management rather than editing internal storage.

## What has and has not been built

Included: original prompts, operating guidance, the custom planning specification, local-setup template, runtime acceptance scenarios, public-source validation scripts, and reproducible packaging.

Not included: authenticated data collectors, a production responsibility database, runtime permission enforcement, account authorization, a deployed gateway, or a verified delivery adapter. Repository unit tests validate packaging and consistency only. The 18 runtime acceptance scenarios are procedures to execute in a real deployment; they are not claimed to have passed there.

Public sources are linked rather than vendored. Names and marks belong to their owners. The MIT license covers original repository material only.
