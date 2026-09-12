# OpenAI Skill And Prompt Guidance

## 2026-09-12 - Instruction calibration

- Sources: OpenAI's September 11, 2026
  [skills and prompts article](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
  and [Astra model guidance](https://developers.openai.com/api/docs/guides/latest-model),
  retrieved through official-domain web browsing.
- Scope: skill discovery, instruction structure, authorization, and completion.
- Finding: concise, discriminating descriptions and conditional references
  reduce irrelevant guidance. Task prompts should define outcomes and real
  boundaries; fixed procedures need a concrete reason. Calibrate testing and
  continuation instructions to the work and models in use.
- Application: reconcile GOATED's inconsistent defaults while preserving
  explicit constraints and portable fallbacks. Expected behavioral benefits
  require evaluation; a shorter instruction is not proof of better results.
- Freshness: recheck for future model migrations or changed host behavior.
  This note is dated evidence, not an automatically refreshed policy.
