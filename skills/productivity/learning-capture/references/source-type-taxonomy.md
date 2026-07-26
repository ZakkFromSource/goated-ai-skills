# Source Type Taxonomy

## Contents

- [Compact Defaults](#compact-defaults)
- [Extended Optional Values](#extended-optional-values)
- [Selection Notes](#selection-notes)

`source_type` is controlled but user-extensible.

Use this order:

1. Use the source-type taxonomy configured by the user, project, or vault.
2. If no taxonomy is configured, use a compact default value that clearly describes the evidence.
3. If no value fits, choose the closest clear value and explain the ambiguity in `source` or `confidence_reason`.
4. Avoid inventing near-duplicates such as `doc`, `docs`, and `documentation` for the same source family.

## Compact Defaults

These values are enough for many agent workflows:

- `conversation`
- `documentation`
- `github`
- `software`
- `experiment`
- `observation`
- `reference`
- `article`
- `book`
- `course`
- `paper`
- `research_paper`
- `website`
- `ai`
- `me`
- `mixed`

## Extended Optional Values

The following list is an optional reference taxonomy for broader personal knowledge systems. Do not force every project to use it.

- `4chan`
- `advertisement`
- `ai`
- `album`
- `app`
- `archive`
- `article`
- `artwork`
- `audio`
- `billboard`
- `blog`
- `book`
- `brochure`
- `catalog`
- `chart`
- `clipping`
- `conference`
- `conversation`
- `course`
- `database`
- `data_set`
- `diary`
- `dictionary`
- `discussion`
- `dissertation`
- `documentary`
- `documentation`
- `drawing`
- `email`
- `encyclopedia`
- `essay`
- `exhibition`
- `experiment`
- `field_notes`
- `film`
- `flyer`
- `forum`
- `gallery`
- `game`
- `github`
- `government_document`
- `graph`
- `guide`
- `illustration`
- `image`
- `instagram`
- `interview`
- `journal`
- `lab_notes`
- `law`
- `lecture`
- `letter`
- `magazine`
- `manual`
- `manuscript`
- `map`
- `me`
- `menu`
- `model`
- `movie`
- `museum`
- `music`
- `neocities`
- `newspaper`
- `notebook`
- `observation`
- `painting`
- `pamphlet`
- `panel`
- `paper`
- `patent`
- `performance`
- `photograph`
- `play`
- `podcast`
- `poem`
- `policy`
- `post`
- `presentation`
- `publication`
- `radio`
- `recording`
- `reddit`
- `reference`
- `regulation`
- `report`
- `research_paper`
- `sculpture`
- `show`
- `signal`
- `simulation`
- `sms`
- `social_media`
- `software`
- `song`
- `specification`
- `speech`
- `standard`
- `talk`
- `telegram`
- `thesis`
- `tiktok`
- `transcript`
- `tutorial`
- `twitter`
- `video`
- `vodcast`
- `webinar`
- `website`
- `whatsapp`
- `white_paper`
- `workshop`
- `x`
- `youtube`

## Selection Notes

- Use `documentation` for official or project docs unless a configured taxonomy distinguishes `official_docs`.
- Use `github` when the source is a GitHub issue, PR, discussion, repository, or release page.
- Use `software` when the evidence is behavior observed in an app, library, CLI, or codebase and no narrower configured value exists.
- Use `experiment` when the lesson came from a deliberate test or prototype.
- Use `observation` when the source is direct observation without a formal experiment.
- Use `ai` only when the lesson came primarily from AI output. Prefer a stronger source when the AI output was verified against docs, code, or experiments.
- Use `me` for the user's own reflection, decision, or memory when the user wants that captured.
- Use `mixed` when multiple source families materially support the note; list the specific evidence in `source`.
