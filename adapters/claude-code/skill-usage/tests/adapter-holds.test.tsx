// Every hold the GOATED Claude Code adapter emits, as the mod records it: its
// gate and kind, what it asks for, and what became of it (followed, declined
// with a reason, or ignored). The hold texts are the adapter's own, generated
// into adapter-texts.ts. Pre-tool holds arrive as errored tool results and the
// closeout hold as a blocked `Stop`; the shapes of both, live and in rebuilt
// history, come from a headless run on Claude Code 2.1.325.

import { expect, test } from 'claude-code/testing'

import type { UsageEvent } from '../types'
import { historyEvents, hookEvents, isObservedRow, markerEvents, rowEvents, summarize, toolUseEvents } from '../hooks/classify'
import type { HistoryMessage, Row } from '../hooks/classify'
import { hookName } from '../hooks/meaning'
import { ADAPTER_TEXTS } from './adapter-texts'

const SKILLS = ['using-goated-ai-skills', 'tdd', 'doc-sync', 'commit-message', 'pr-description', 'handoff', 'subagent-driven-development', 'software-design-principles', 'code-security-review', 'resolving-merge-conflicts']

const denied = (tool: string, text: string) => `PreToolUse:${tool} hook error: ${text}`
// A blocked Stop, as both a live hook-context row and the rebuilt history carry it (the run's command path aside).
const STOP_COMMAND = 'python /tools/goated-adapter/goated_hook.py'
const blockedStop = (reason: string, eol = '\n') => `<system-reminder>${eol}Stop hook blocking error from command: "${STOP_COMMAND}": ${reason.split('\n').join(eol)}${eol}</system-reminder>`

const prompt = (t = 1): UsageEvent => ({ kind: 'prompt', t, named: [] })
const response = (t: number): UsageEvent => ({ kind: 'response', t })
const results = (t: number): UsageEvent => ({ kind: 'results', t })
const load = (skill: string, t: number): UsageEvent => ({ kind: 'load', t, skill, via: 'tool', isSubagent: false })
const preHold = (tool: string, text: string, t: number) => hookEvents(denied(tool, text), t, { holdsOnly: true })
const stopHold = (t: number, text: string = ADAPTER_TEXTS.closeout) => hookEvents(blockedStop(text), t)
const turnEnd = (t: number): UsageEvent => ({ kind: 'turn-end', t })

const row = (door: string, content: Row['message']['content'], more: Partial<Row['message']> & { agentId?: string } = {}): Row => {
  const { agentId, ...message } = more
  return { door, ...(agentId ? { agentId } : {}), message: { content, ...message } }
}

// ---------- what each hold is and asks for ------------------------------------------

test('each action hold reads as its gate and kind and names the skills it asks for', async () => {
  const cases: [string, string, string, string, string[]][] = [
    ['commit', 'Bash', ADAPTER_TEXTS.commit, 'strict', ['commit-message']],
    ['pull-request', 'Bash', ADAPTER_TEXTS.pullRequest, 'strict', ['pr-description']],
    ['pr-review', 'Bash', ADAPTER_TEXTS.prReview, 'justified-skip', ['standards-and-spec-review']],
    ['spawn', 'Agent', ADAPTER_TEXTS.spawn, 'strict', ['handoff', 'subagent-driven-development']],
    ['design', 'Write', ADAPTER_TEXTS.design, 'justified-skip', ['software-design-principles']],
    ['security', 'Write', ADAPTER_TEXTS.security, 'justified-skip', ['code-security-review']],
    // A file with no extension is quoted, not backticked, so it is no skill.
    ['security', 'Write', ADAPTER_TEXTS.securityNoExtension, 'justified-skip', ['code-security-review']],
    // A shell write is held like a write tool's.
    ['security', 'Bash', ADAPTER_TEXTS.shellWrite, 'justified-skip', ['code-security-review']],
    ['conflict-resolution', 'Edit', ADAPTER_TEXTS.conflictResolution, 'justified-skip', ['resolving-merge-conflicts']],
    // After a reviewer subagent reports, fixes start with the intake skill (Ticket 070).
    ['review-intake', 'Edit', ADAPTER_TEXTS.reviewIntake, 'justified-skip', ['receiving-code-review']],
    // The quoted check command it names is no skill.
    ['repeated-failure', 'Edit', ADAPTER_TEXTS.repeatedFailure, 'justified-skip', ['diagnose']],
    // An inline script that writes a code file asks for a file edit tool, or a design skip (Ticket 093).
    ['scripted-edit', 'Bash', ADAPTER_TEXTS.scriptedEdit, 'justified-skip', ['software-design-principles']],
  ]
  for (const [gate, tool, text, kind, named] of cases) {
    expect(preHold(tool, text, 1)).toEqual([expect.objectContaining({ kind: 'nudge', hook: gate, holdKind: kind, named })])
  }
  expect(hookName('review-intake')).toBe('review-intake hold')
  expect(hookName('scripted-edit')).toBe('scripted-edit hold')
})

test('holds that ask for a read, missing headings or a message fix name no skill, so they count by gate and kind alone', async () => {
  for (const [tool, text, gate] of [
    ['Agent', ADAPTER_TEXTS.spawnRead, 'spawn'],
    ['Agent', ADAPTER_TEXTS.spawnHeadings, 'spawn'],
    ['Agent', ADAPTER_TEXTS.spawnStatus, 'spawn'],
    ['Bash', ADAPTER_TEXTS.commitContract, 'commit'],
    ['Bash', ADAPTER_TEXTS.commitRead, 'commit'],
    ['Bash', ADAPTER_TEXTS.pullRequestRead, 'pull-request'],
  ] as const) {
    expect(preHold(tool, text, 1)).toEqual([{ kind: 'nudge', t: 1, hook: gate, named: [], holdKind: 'strict' }])
    const s = summarize([prompt(), ...preHold(tool, text, 2), turnEnd(3)])
    expect(s.holds).toEqual({ strict: 1 })
    expect(s.nudges).toEqual({})
    const nudge = s.timeline.find(e => e.kind === 'nudge')
    expect(nudge?.kind === 'nudge' && nudge.skills).toEqual([])
  }
})

test('the pr-review change-read hold names no skill, so a read that clears it is not counted as ignored', async () => {
  expect(preHold('Bash', ADAPTER_TEXTS.prReviewRead, 1)).toEqual([{ kind: 'nudge', t: 1, hook: 'pr-review', named: [], holdKind: 'justified-skip' }])
  const s = summarize([prompt(), ...preHold('Bash', ADAPTER_TEXTS.prReviewRead, 2), turnEnd(3)])
  expect(s.holds).toEqual({ 'justified-skip': 1 })
  expect(s.nudges).toEqual({})
})

test('the pr-review hold reads under its own name', async () => {
  expect(hookName('pr-review')).toBe('pr-review hold')
})

// ---------- the closeout hold, a blocked Stop ---------------------------------------

test('the closeout hold reads from the blocked Stop that carries it, live and in history, once each', async () => {
  // The proof item asks for a check to run, or a skip line naming the verification skill, so it names that skill.
  const want = [{ kind: 'nudge', t: 1, hook: 'closeout', named: ['verification-before-completion', 'doc-sync'], holdKind: 'justified-skip', isStop: true, skipOnly: ['verification-before-completion'], items: [{ label: 'Proof', skill: 'verification-before-completion' }, { label: 'Docs', skill: 'doc-sync' }] }]
  const live = row('hook-context', [{ type: 'text', text: blockedStop(ADAPTER_TEXTS.closeout) }], { name: 'hook_blocking_error' })
  // A blocked Stop hands the agent its reason as a tool result would, so it ends the reply's round trip.
  expect(rowEvents(live, SKILLS, 1, { lastBoundary: 'response' })).toEqual([...want, { kind: 'results', t: 1 }])
  expect(rowEvents(live, SKILLS, 1, { lastBoundary: 'results' })).toEqual(want)
  // History holds the same reminder, after the reply it blocked; the plain "Stop hook feedback" note is not in it.
  const history: HistoryMessage[] = [
    { role: 'user', content: [{ type: 'text', text: 'Fix the exporter.' }] },
    { role: 'assistant', content: [{ type: 'text', text: 'Done.' }] },
    { role: 'user', content: [{ type: 'text', text: blockedStop(ADAPTER_TEXTS.closeout) }] },
  ]
  expect(historyEvents(history, SKILLS, 1).filter(e => e.kind === 'nudge')).toEqual(want.map(e => ({ ...e, isEarlier: true })))
  expect(historyEvents(history, SKILLS, 1).map(e => e.kind)).toEqual(['prompt', 'response', 'nudge', 'results'])
  // Line ends written as CRLF read the same.
  expect(hookEvents(blockedStop(ADAPTER_TEXTS.closeout, '\r\n'), 1)).toEqual(want)
})

test('the closeout hold is read once live: the plain feedback note row is not observed', async () => {
  const note = row('note', [{ type: 'text', text: `Stop hook feedback:\n${ADAPTER_TEXTS.closeout}` }], { type: 'user', isMeta: true })
  expect(isObservedRow(note)).toBe(false)
})

test('the closeout hold names each skill its items ask for, those named only in their skip line too, and not the red-flags path', async () => {
  expect(stopHold(1, ADAPTER_TEXTS.closeoutUnfinished)).toEqual([{ kind: 'nudge', t: 1, hook: 'closeout', named: ['handoff', 'doc-sync', 'software-design-principles'], holdKind: 'justified-skip', isStop: true, skipOnly: ['software-design-principles'], items: [{ label: 'Unfinished', skill: 'handoff' }, { label: 'Docs', skill: 'doc-sync' }, { label: 'Design', skill: 'software-design-principles' }] }])
})

test('a hold line is a hold only as an errored result or a blocked Stop: other hook text that carries one is not', async () => {
  expect(hookEvents(`SessionStart hook additional context: see the log:\n${ADAPTER_TEXTS.closeout}`, 1)).toEqual([])
  expect(hookEvents(`<system-reminder>\n${ADAPTER_TEXTS.design}\n</system-reminder>`, 1)).toEqual([])
  expect(hookEvents(`Stop hook feedback:\n${ADAPTER_TEXTS.design}`, 1)).toEqual([])
  expect(hookEvents(blockedStop('Tests are failing; fix them first.'), 1)).toEqual([])
})

// ---------- strict holds: only loading clears them, in the turn they ask ------------

for (const [gate, tool, text, skill] of [
  ['commit', 'Bash', ADAPTER_TEXTS.commit, 'commit-message'],
  ['pull-request', 'Bash', ADAPTER_TEXTS.pullRequest, 'pr-description'],
] as const) {
  test(`the ${gate} hold is followed by loading ${skill}`, async () => {
    const s = summarize([prompt(), ...preHold(tool, text, 2), load(skill, 3), turnEnd(4)])
    expect(s.nudges).toEqual({ [gate]: { followed: 1 } })
    expect(s.holds).toEqual({ strict: 1 })
  })

  test(`the ${gate} hold is ignored when the turn ends without ${skill}, and a skip line never declines it`, async () => {
    const s = summarize([prompt(), ...preHold(tool, text, 2), ...markerEvents(`goated-skip: ${skill}: the message was typed by the user`, 3), turnEnd(4)])
    expect(s.nudges).toEqual({ [gate]: { unanswered: 1 } })
    const early = summarize([prompt(), ...markerEvents(`goated-skip: ${skill}: the message was typed by the user`, 2), ...preHold(tool, text, 3), turnEnd(4)])
    expect(early.nudges).toEqual({ [gate]: { unanswered: 1 } })
  })

  test(`a ${gate} hold shown after ${skill} loaded in an earlier turn is not "already loaded"`, async () => {
    const s = summarize([prompt(1), load(skill, 2), turnEnd(3), prompt(4), ...preHold(tool, text, 5), load(skill, 6), turnEnd(7)])
    expect(s.nudges).toEqual({ [gate]: { followed: 1 } })
  })
}

test('the spawn hold asks once for either brief skill: loading one follows it, and leaving both counts it ignored once', async () => {
  const sdd = summarize([prompt(), ...preHold('Agent', ADAPTER_TEXTS.spawn, 2), load('subagent-driven-development', 3), turnEnd(4)])
  expect(sdd.nudges).toEqual({ spawn: { followed: 1 } })
  const nudge = sdd.timeline.find(e => e.kind === 'nudge')
  expect(nudge?.kind === 'nudge' && nudge.skills).toEqual([{ skill: 'subagent-driven-development', status: 'followed', at: 3 }])
  expect(summarize([prompt(), ...preHold('Agent', ADAPTER_TEXTS.spawn, 2), load('handoff', 3), turnEnd(4)]).nudges).toEqual({ spawn: { followed: 1 } })
  const neither = summarize([prompt(), ...preHold('Agent', ADAPTER_TEXTS.spawn, 2), turnEnd(3)])
  expect(neither.nudges).toEqual({ spawn: { unanswered: 1 } })
  const waiting = neither.timeline.find(e => e.kind === 'nudge')
  expect(waiting?.kind === 'nudge' && waiting.skills).toEqual([{ skill: 'handoff or subagent-driven-development', status: 'unanswered', at: 3 }])
  // A load in an earlier turn, before the hold, does not answer it.
  const later = summarize([prompt(1), load('handoff', 2), turnEnd(3), prompt(4), ...preHold('Agent', ADAPTER_TEXTS.spawn, 5), load('handoff', 6), turnEnd(7)])
  expect(later.nudges).toEqual({ spawn: { followed: 1 } })
})

// ---------- a load counts only when it ran ------------------------------------------

test('a Skill call whose result is an error loaded nothing: it neither counts nor answers a hold', async () => {
  const call = toolUseEvents([{ id: 'u1', name: 'Skill', input: { skill: 'software-design-principles' } }], false, 3)
  const s = summarize([prompt(), ...preHold('Write', ADAPTER_TEXTS.design, 2), ...call, { kind: 'refused', t: 4, id: 'u1' }, turnEnd(5)])
  expect(s.loads).toEqual({})
  expect(s.nudges).toEqual({ design: { unanswered: 1 } })
  expect(s.timeline.some(e => e.kind === 'load')).toBe(false)
  // The same call with a result that is no error loaded the skill.
  expect(summarize([prompt(), ...preHold('Write', ADAPTER_TEXTS.design, 2), ...call, turnEnd(5)]).nudges).toEqual({ design: { followed: 1 } })
})

test('a Skill call names its skill as the adapter reads it: no leading slash, no arguments', async () => {
  const [load] = toolUseEvents([{ id: 'u1', name: 'Skill', input: { skill: '/tdd write the failing test first' } }], false, 1)
  expect(load).toEqual({ kind: 'load', t: 1, id: 'u1', skill: 'tdd', via: 'tool', isSubagent: false })
})

// ---------- a hold the held call's own reply already answered ----------------------

test("a route line in the held call's own reply answers its route-line hold, which Claude Code shows the adapter one call late", async () => {
  const s = summarize([
    prompt(),
    response(2), ...markerEvents('goated-route: direct', 2), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 3), results(3),
    turnEnd(4),
  ])
  expect(s.nudges).toEqual({ 'route-line': { followed: 1 } })
})

test('a route line in an earlier reply, or from an earlier prompt, does not answer a later route-line hold', async () => {
  const earlierReply = summarize([
    prompt(),
    response(2), ...markerEvents('goated-route: direct', 2), results(2),
    response(3), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 3), results(3),
    turnEnd(4),
  ])
  expect(earlierReply.nudges).toEqual({ 'route-line': { unanswered: 1 } })
  const earlierPrompt = summarize([prompt(), ...markerEvents('goated-route: direct', 2), prompt(3), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 4), turnEnd(5)])
  expect(earlierPrompt.nudges).toEqual({ 'route-line': { unanswered: 1 } })
})

test('a `continue` route line with no task to continue answers no route-line hold, in the same reply or later', async () => {
  const noTask = 'goated-hold: route-line | strict\n`goated-route: continue` was written, but this session has no current task to continue. Write the route line the router selects for this task.'
  const s = summarize([
    prompt(),
    response(2), ...markerEvents('goated-route: continue', 2), ...preHold('Edit', noTask, 3), results(3),
    response(4), ...markerEvents('goated-route: continue', 4),
    turnEnd(5),
  ])
  expect(s.nudges).toEqual({ 'route-line': { unanswered: 1 } })
  // Once a task exists, `continue` is a route line like any other.
  const withTask = summarize([prompt(1), ...markerEvents('goated-route: direct', 1), prompt(2), response(3), ...markerEvents('goated-route: continue', 3), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 4), turnEnd(5)])
  expect(withTask.nudges).toEqual({ 'route-line': { followed: 1 } })
})

test("a skill loaded beside the held call in its own reply answers the hold, even after the reply's other results came back", async () => {
  const s = summarize([
    prompt(),
    response(2), load('commit-message', 2), results(3), ...preHold('Bash', ADAPTER_TEXTS.commit, 3),
    turnEnd(4),
  ])
  expect(s.nudges).toEqual({ commit: { followed: 1 } })
})

test('reply and result rows mark where a main round trip begins, once each; subagent rows do not', async () => {
  const text = row('response', [{ type: 'text', text: 'goated-route: direct' }])
  expect(rowEvents(text, SKILLS, 1, { lastBoundary: 'results' })).toEqual([{ kind: 'response', t: 1 }, { kind: 'route', t: 1, form: 'direct' }])
  expect(rowEvents(text, SKILLS, 1, { lastBoundary: 'response' })).toEqual([{ kind: 'route', t: 1, form: 'direct' }])
  const ok = row('tool-result', [{ type: 'tool_result', tool_use_id: 'u1', content: 'ok', is_error: false }])
  expect(rowEvents(ok, SKILLS, 2, { lastBoundary: 'response' })).toEqual([{ kind: 'results', t: 2 }])
  expect(rowEvents(ok, SKILLS, 2, { lastBoundary: 'results' })).toEqual([])
  const heldRow = row('tool-result', [{ type: 'tool_result', tool_use_id: 'u2', content: denied('Edit', ADAPTER_TEXTS.routeLine), is_error: true }])
  expect(rowEvents(heldRow, SKILLS, 3, { lastBoundary: 'response' }).map(e => e.kind)).toEqual(['nudge', 'refused', 'results'])
  expect(rowEvents({ ...text, agentId: 'a1' }, SKILLS, 1, { lastBoundary: 'results' }).map(e => e.kind)).toEqual(['route'])
  // History marks each assistant message and each message of results.
  const history: HistoryMessage[] = [
    { role: 'user', content: [{ type: 'text', text: 'Fix it.' }] },
    { role: 'assistant', content: [{ type: 'text', text: 'goated-route: direct' }, { type: 'tool_use', id: 'u1', name: 'Bash', input: { command: 'ls' } }] },
    { role: 'user', content: [{ type: 'tool_result', tool_use_id: 'u1', content: 'ok' }] },
  ]
  expect(historyEvents(history, SKILLS, 1).map(e => e.kind)).toEqual(['prompt', 'response', 'route', 'results'])
})

// ---------- justified-skip holds: followed, declined with a reason, or ignored -------

for (const [gate, tool, text, skill] of [
  ['design', 'Write', ADAPTER_TEXTS.design, 'software-design-principles'],
  ['security', 'Write', ADAPTER_TEXTS.security, 'code-security-review'],
  ['security', 'Bash', ADAPTER_TEXTS.shellWrite, 'code-security-review'],
  ['conflict-resolution', 'Edit', ADAPTER_TEXTS.conflictResolution, 'resolving-merge-conflicts'],
  ['repeated-failure', 'Edit', ADAPTER_TEXTS.repeatedFailure, 'diagnose'],
  ['pr-review', 'Bash', ADAPTER_TEXTS.prReview, 'standards-and-spec-review'],
  ['review-intake', 'Edit', ADAPTER_TEXTS.reviewIntake, 'receiving-code-review'],
] as const) {
  const reason = 'the edit changes one constant and nothing else'
  test(`the ${gate} hold on ${tool} is followed by loading ${skill}, declined by a skip line with its reason, and otherwise ignored`, async () => {
    const followed = summarize([prompt(), ...preHold(tool, text, 2), load(skill, 3), turnEnd(4)])
    expect(followed.nudges).toEqual({ [gate]: { followed: 1 } })

    const declined = summarize([prompt(), ...preHold(tool, text, 2), ...markerEvents(`goated-skip: ${skill}: ${reason}`, 3), turnEnd(4)])
    expect(declined.nudges).toEqual({ [gate]: { declined: 1 } })
    const nudge = declined.timeline.find(e => e.kind === 'nudge')
    expect(nudge?.kind === 'nudge' && nudge.holdKind).toBe('justified-skip')
    expect(nudge?.kind === 'nudge' && nudge.skills).toEqual([{ skill, status: 'declined', at: 3, reason }])

    const ignored = summarize([prompt(), ...preHold(tool, text, 2), turnEnd(3)])
    expect(ignored.nudges).toEqual({ [gate]: { unanswered: 1 } })
    expect(ignored.holds).toEqual({ 'justified-skip': 1 })
  })
}

test('the scripted-edit hold asks for a file edit tool: a code edit after it follows it, a load of the skill it offers to skip does not', async () => {
  const text = ADAPTER_TEXTS.scriptedEdit
  expect(preHold('Bash', text, 1)).toEqual([expect.objectContaining({ hook: 'scripted-edit', named: ['software-design-principles'], skipOnly: ['software-design-principles'] })])
  const followed = summarize([prompt(), ...preHold('Bash', text, 2), { kind: 'change', t: 3, id: 'w1' }, turnEnd(4)])
  expect(followed.nudges).toEqual({ 'scripted-edit': { followed: 1 } })
  // A refused edit changed nothing, so it follows nothing.
  const refused = summarize([prompt(), ...preHold('Bash', text, 2), { kind: 'change', t: 3, id: 'w1' }, { kind: 'refused', t: 3, id: 'w1' }, turnEnd(4)])
  expect(refused.nudges).toEqual({ 'scripted-edit': { unanswered: 1 } })
  const loaded = summarize([prompt(), ...preHold('Bash', text, 2), load('software-design-principles', 3), turnEnd(4)])
  expect(loaded.nudges).toEqual({ 'scripted-edit': { unanswered: 1 } })
  const reason = 'one mechanical rename across forty files'
  const declined = summarize([prompt(), ...preHold('Bash', text, 2), ...markerEvents(`goated-skip: software-design-principles: ${reason}`, 3), turnEnd(4)])
  expect(declined.nudges).toEqual({ 'scripted-edit': { declined: 1 } })
})

test('the repeated-failure hold has its own name and counts, apart from the earlier hooks\' diagnose key', async () => {
  expect(hookName('repeated-failure')).toBe('repeated-failure hold')
  expect(hookName('diagnose')).toBe('repeated failure')
  const s = summarize([prompt(), ...preHold('Edit', ADAPTER_TEXTS.repeatedFailure, 2), load('diagnose', 3), turnEnd(4)])
  expect(s.nudges).toEqual({ 'repeated-failure': { followed: 1 } })
})

test('a security hold on a file named like a word, as adapters before 034 backticked it, still names only the review skill', async () => {
  const old = ADAPTER_TEXTS.security.replace('"auth.py"', '`login`').replace('a goated-skip line', 'a `goated-skip` line')
  expect(preHold('Write', old, 1)).toEqual([expect.objectContaining({ named: expect.arrayContaining(['code-security-review']) })])
})

test('the closeout hold is followed by loading the skill it names, declined by a skip line with its reason, and otherwise ignored', async () => {
  // The docs item alone, so each case turns on doc-sync.
  const docsOnly = ADAPTER_TEXTS.closeout.replace(/\n- Proof:[^\n]*/, '')
  const followed = summarize([prompt(), ...stopHold(2, docsOnly), load('doc-sync', 3), turnEnd(4)])
  expect(followed.nudges).toEqual({ closeout: { followed: 1 } })
  const reason = 'the change touches behavior no doc describes'
  const declined = summarize([prompt(), ...stopHold(2, docsOnly), ...markerEvents(`goated-skip: doc-sync: ${reason}`, 3), turnEnd(4)])
  expect(declined.nudges).toEqual({ closeout: { declined: 1 } })
  const nudge = declined.timeline.find(e => e.kind === 'nudge' && e.hook === 'closeout')
  expect(nudge?.kind === 'nudge' && nudge.skills).toEqual([{ skill: 'doc-sync', status: 'declined', at: 3, reason }])
  const ignored = summarize([prompt(), ...stopHold(2, docsOnly), turnEnd(3)])
  expect(ignored.nudges).toEqual({ closeout: { unanswered: 1 } })
  expect(ignored.holds).toEqual({ 'justified-skip': 1 })
})

test('the closeout Setup item asks for setup-scribe: a load follows it, a skip line declines it, and otherwise it is ignored', async () => {
  const text = ADAPTER_TEXTS.closeoutSetup
  expect(stopHold(1, text)).toEqual([{ kind: 'nudge', t: 1, hook: 'closeout', named: ['setup-scribe'], holdKind: 'justified-skip', isStop: true, items: [{ label: 'Setup', skill: 'setup-scribe' }] }])
  expect(summarize([prompt(), ...stopHold(2, text), load('setup-scribe', 3), turnEnd(4)]).nudges).toEqual({ closeout: { followed: 1 } })
  const reason = 'the lockfile already records it'
  const declined = summarize([prompt(), ...stopHold(2, text), ...markerEvents(`goated-skip: setup-scribe: ${reason}`, 3), turnEnd(4)])
  expect(declined.nudges).toEqual({ closeout: { declined: 1 } })
  const nudge = declined.timeline.find(e => e.kind === 'nudge' && e.hook === 'closeout')
  expect(nudge?.kind === 'nudge' && nudge.skills).toEqual([{ skill: 'setup-scribe', status: 'declined', at: 3, reason }])
  expect(summarize([prompt(), ...stopHold(2, text), turnEnd(3)]).nudges).toEqual({ closeout: { unanswered: 1 } })
})

test('the closeout Review and Verification items ask for their skills by label, the reviewer prompt path aside', async () => {
  // Ticket 069: a large branch's turn. The reviewer prompt is named by its path, so it reads as no skill.
  const text = ADAPTER_TEXTS.closeoutReview
  expect(stopHold(1, text)).toEqual([{ kind: 'nudge', t: 1, hook: 'closeout', named: ['standards-and-spec-review', 'verification-before-completion'], holdKind: 'justified-skip', isStop: true, items: [{ label: 'Review', skill: 'standards-and-spec-review' }, { label: 'Verification', skill: 'verification-before-completion' }] }])
  const followed = summarize([prompt(), ...stopHold(2, text), load('standards-and-spec-review', 3), load('verification-before-completion', 4), turnEnd(5)])
  expect(followed.nudges).toEqual({ closeout: { followed: 2 } })
  expect(followed.closeoutItems).toEqual({ Review: { followed: 1 }, Verification: { followed: 1 } })
})

test('a blocked Stop does not end the turn: blocks in a row are one hold, and the load that follows answers it once', async () => {
  const s = summarize([prompt(), response(1), ...stopHold(2), results(2), response(3), ...stopHold(4), results(4), response(5), load('doc-sync', 5), results(6), turnEnd(7)])
  expect(s.nudges.closeout).toEqual({ followed: 2 })
  expect(s.holds).toEqual({ 'justified-skip': 2 })
  const rows = s.timeline.filter(e => e.kind === 'nudge')
  expect(rows).toHaveLength(1)
  expect(rows[0]?.kind === 'nudge' && rows[0].repeats).toBe(2)
})

test('a turn that ends after the agent answered a blocked Stop passed the closeout: what it still asked counts as followed', async () => {
  // The adapter judges every Stop: a reply after the block that ends the turn without another block met each item,
  // by a check run, a fix, a load or a skip line. The proof item asks for a check run, which is no load.
  const passed = summarize([prompt(), response(1), ...stopHold(2, ADAPTER_TEXTS.closeoutUnfinished), results(2), response(3), turnEnd(4)])
  expect(passed.nudges).toEqual({ closeout: { followed: 3 } })
  // A skip line still declines its own item, with its reason.
  const reason = 'no test runner exists in this folder'
  const skipped = summarize([prompt(), response(1), ...stopHold(2), results(2), response(3), ...markerEvents(`goated-skip: verification-before-completion: ${reason}`, 3), turnEnd(4)])
  expect(skipped.nudges).toEqual({ closeout: { declined: 1, followed: 1 } })
  // With no reply after the block, the turn did not get past it.
  expect(summarize([prompt(), response(1), ...stopHold(2), results(2), turnEnd(3)]).nudges).toEqual({ closeout: { unanswered: 2 } })
})

test('a closeout hold on a commit counts as one on a Stop: a turn that then ends as an answer met what it asked', async () => {
  // The commit-time closeout (Ticket 059) asks for the same items; the Stop that ends the turn judges them all again.
  expect(preHold('Bash', ADAPTER_TEXTS.closeoutCommit, 1)).toEqual([{ kind: 'nudge', t: 1, hook: 'closeout', named: ['verification-before-completion', 'doc-sync'], holdKind: 'justified-skip', skipOnly: ['verification-before-completion'], items: [{ label: 'Proof', skill: 'verification-before-completion' }, { label: 'Docs', skill: 'doc-sync' }] }])
  const committed = [prompt(), response(1), ...preHold('Bash', ADAPTER_TEXTS.closeoutCommit, 2), results(2), response(3)]
  expect(summarize([...committed, turnEnd(4)]).nudges).toEqual({ closeout: { followed: 2 } })
  // A skip line still declines its own item, with its reason.
  const reason = 'no test runner exists in this folder'
  const skipped = summarize([...committed, ...markerEvents(`goated-skip: verification-before-completion: ${reason}`, 3), turnEnd(4)])
  expect(skipped.nudges).toEqual({ closeout: { declined: 1, followed: 1 } })
  // A turn the user stopped did not get past it.
  expect(summarize([...committed, { kind: 'turn-end', t: 4, reason: 'aborted' }]).nudges).toEqual({ closeout: { 'new prompt': 2 } })
  // A blocked Stop after it joins its row; a Stop that blocks the turn's end at the limit leaves its asks unmet.
  const stopped = summarize([...committed, ...stopHold(4), results(4), response(5), turnEnd(6)])
  expect(stopped.nudges).toEqual({ closeout: { followed: 2 } })
  expect(stopped.timeline.filter(e => e.kind === 'nudge')).toHaveLength(1)
})

test('a closeout hold on a commit, like one on a Stop, has judged the skip lines before it: one it still asks past is no decline', async () => {
  // The adapter held past this skip line (it may not have seen it: reply text can be stored as a summary), so the
  // item it names is still unmet.
  const skip = markerEvents('goated-skip: verification-before-completion: no test suite here', 2)
  const held = summarize([prompt(), response(1), ...skip, ...preHold('Bash', ADAPTER_TEXTS.closeoutCommit, 3), results(3), { kind: 'turn-end', t: 4, reason: 'aborted' }])
  expect(held.nudges).toEqual({ closeout: { 'new prompt': 2 } })
  // Another gate's call hold still counts an earlier skip line as its decline.
  const design = summarize([prompt(), response(1), ...markerEvents('goated-skip: software-design-principles: one mechanical constant change', 2), ...preHold('Write', ADAPTER_TEXTS.design, 3), turnEnd(4)])
  expect(design.nudges).toEqual({ design: { declined: 1 } })
})

test('closeout items that ask for a read of the change offer their skills only as skip lines, and a passed Stop meets them', async () => {
  // The skills are loaded, so each item asks for a read of the change, which no load answers.
  const named = ['doc-sync', 'software-design-principles', 'code-security-review']
  const items = [{ label: 'Docs', skill: 'doc-sync' }, { label: 'Design', skill: 'software-design-principles' }, { label: 'Security', skill: 'code-security-review' }]
  expect(stopHold(1, ADAPTER_TEXTS.closeoutChangeRead)).toEqual([{ kind: 'nudge', t: 1, hook: 'closeout', named, holdKind: 'justified-skip', isStop: true, skipOnly: named, items }])
  const passed = summarize([prompt(), response(1), ...stopHold(2, ADAPTER_TEXTS.closeoutChangeRead), results(2), response(3), turnEnd(4)])
  expect(passed.nudges).toEqual({ closeout: { followed: 3 } })
})

test('a turn that ends after nine blocked Stops in a row hit the Claude Code limit: what was still asked counts as not followed', async () => {
  const blocks = Array.from({ length: 9 }, (_, i) => [...stopHold(2 + 2 * i), results(2 + 2 * i), response(3 + 2 * i)]).flat()
  const s = summarize([prompt(), response(1), ...blocks, turnEnd(30)])
  expect(s.nudges).toEqual({ closeout: { unanswered: 2 } })
  expect(s.holds).toEqual({ 'justified-skip': 9 })
})

test('a hold repeated in the turn while its asks still wait is one row counted once; a different ask is a row of its own', async () => {
  const routeHolds = summarize([
    prompt(),
    response(1), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 2), results(2),
    response(3), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 3), results(3),
    response(4), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 4), results(4),
    response(5), ...markerEvents('goated-route: direct', 5),
    turnEnd(6),
  ])
  expect(routeHolds.nudges).toEqual({ 'route-line': { followed: 1 } })
  expect(routeHolds.holds).toEqual({ strict: 3 })
  const rows = routeHolds.timeline.filter(e => e.kind === 'nudge')
  expect(rows.map(e => e.kind === 'nudge' && e.repeats)).toEqual([3])
  // A pipeline hold that asks again for what is still missing joins the row; what it no longer asks for was met.
  const pipeline = summarize([prompt(), ...preHold('Edit', ADAPTER_TEXTS.pipeline, 2), load('tdd', 3), ...preHold('Edit', ADAPTER_TEXTS.pipeline.replace('`tdd`, ', ''), 4), turnEnd(5)])
  expect(pipeline.nudges).toEqual({ pipeline: { followed: 1, unanswered: 1 } })
  expect(pipeline.timeline.filter(e => e.kind === 'nudge')).toHaveLength(1)
  // Holds on two different skills of the same gate stay apart.
  const two = summarize([prompt(), ...preHold('Edit', ADAPTER_TEXTS.pipeline.replace('`tdd`, ', ''), 2), ...preHold('Edit', ADAPTER_TEXTS.pipeline.replace(', `doc-sync`', ''), 3), turnEnd(4)])
  expect(two.timeline.filter(e => e.kind === 'nudge')).toHaveLength(2)
  // In the next turn the same hold is a new row.
  const later = summarize([prompt(1), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 2), turnEnd(3), prompt(4), ...preHold('Edit', ADAPTER_TEXTS.routeLine, 5), turnEnd(6)])
  expect(later.timeline.filter(e => e.kind === 'nudge')).toHaveLength(2)
})

// ---------- review probes: how the closeout and repeats count in real runs ----------

const proofOnly = ADAPTER_TEXTS.closeout.replace(/\n- Docs:[^\n]*/, '')
const skipLine = (skill: string, t: number) => markerEvents(`goated-skip: ${skill}: no test runner exists in this folder`, t)
const nudgeRows = (s: ReturnType<typeof summarize>) => s.timeline.flatMap(e => (e.kind === 'nudge' ? [{ repeats: e.repeats, skills: e.skills.map(k => `${k.skill}:${k.status}`) }] : []))

test('a skip line the adapter keeps blocking past is not a decline: nine blocks in a row end the turn not followed', async () => {
  // Ticket 034's run: a skip line, then eight more blocks of the same Stop.
  const events: UsageEvent[] = [prompt(), response(1), ...stopHold(2, proofOnly), results(2), response(3), ...skipLine('verification-before-completion', 3)]
  for (let i = 0; i < 8; i++) events.push(...stopHold(4 + 2 * i, proofOnly), results(4 + 2 * i), response(5 + 2 * i))
  const s = summarize([...events, turnEnd(40)])
  expect(s.nudges).toEqual({ closeout: { unanswered: 1 } })
  expect(s.holds).toEqual({ 'justified-skip': 9 })
  expect(nudgeRows(s)).toEqual([{ repeats: 9, skills: ['verification-before-completion:unanswered'] }])
})

test('the nine-block limit counts every blocked Stop of the turn, whatever each asked', async () => {
  const events: UsageEvent[] = [prompt(), response(1)]
  for (let i = 0; i < 9; i++) events.push(...stopHold(2 + 2 * i, i % 2 === 0 ? proofOnly : ADAPTER_TEXTS.closeout), results(2 + 2 * i), response(3 + 2 * i))
  const s = summarize([...events, turnEnd(40)])
  // The last block asked for proof alone, so the adapter judged docs met; proof was still missing when the limit hit.
  expect(s.nudges).toEqual({ closeout: { unanswered: 1, followed: 1 } })
  expect(nudgeRows(s)).toEqual([{ repeats: 9, skills: ['verification-before-completion:unanswered', 'doc-sync:followed'] }])
})

test('a skill a hold offers only as a skip line is not answered by loading it', async () => {
  // The proof item asks for a check run: loading the verification skill is no proof, and the adapter blocks again.
  const reloaded = summarize([prompt(), response(1), ...stopHold(2, proofOnly), results(2), response(3), load('verification-before-completion', 3), results(3), response(4), ...stopHold(5, proofOnly), results(5)])
  expect(reloaded.nudges).toEqual({ closeout: { pending: 1 } })
  expect(nudgeRows(reloaded)).toEqual([{ repeats: 2, skills: ['verification-before-completion:pending'] }])
  // The design item asks for a read of the red-flags file: loading the design skill again is not that read.
  const design = ADAPTER_TEXTS.closeoutUnfinished.replace(/\n- Unfinished:[^\n]*/, '').replace(/\n- Docs:[^\n]*/, '')
  const loadedAgain = summarize([prompt(), response(1), ...stopHold(2, design), results(2), response(3), load('software-design-principles', 3)])
  expect(loadedAgain.nudges).toEqual({ closeout: { pending: 1 } })
  // A pre-tool hold names its skill to load as well as in its skip line, so loading it still answers that hold.
  expect(summarize([prompt(), ...preHold('Write', ADAPTER_TEXTS.design, 2), load('software-design-principles', 3), turnEnd(4)]).nudges).toEqual({ design: { followed: 1 } })
})

test('a blocked Stop passes only on a turn that ended as an answer, not one interrupted or closed by the next prompt', async () => {
  const blocked = [prompt(), response(1), ...stopHold(2, proofOnly), results(2), response(3)]
  expect(summarize([...blocked, { kind: 'turn-end', t: 4, reason: 'answer' }]).nudges).toEqual({ closeout: { followed: 1 } })
  expect(summarize([...blocked, { kind: 'turn-end', t: 4, reason: 'aborted' }]).nudges).toEqual({ closeout: { 'new prompt': 1 } })
  expect(summarize([...blocked, { kind: 'turn-end', t: 4, reason: 'error' }]).nudges).toEqual({ closeout: { unanswered: 1 } })
  // Rebuilt history has no turn ends: the next prompt closes the turn, and cannot tell a pass from an interruption.
  expect(summarize([...blocked, prompt(4)]).nudges).toEqual({ closeout: { 'new prompt': 1 } })
})

test('a retry held again before the adapter saw the load or skip line beside it joins the row and counts once', async () => {
  const lagLoad = summarize([prompt(), response(1), ...preHold('Edit', ADAPTER_TEXTS.design, 2), results(2), response(3), load('software-design-principles', 3), ...preHold('Edit', ADAPTER_TEXTS.design, 3), results(3), response(4), turnEnd(5)])
  expect(lagLoad.nudges).toEqual({ design: { followed: 1 } })
  expect(nudgeRows(lagLoad)).toEqual([{ repeats: 2, skills: ['software-design-principles:followed'] }])
  const lagSkip = summarize([prompt(), ...preHold('Write', ADAPTER_TEXTS.design, 2), ...skipLine('software-design-principles', 3), ...preHold('Write', ADAPTER_TEXTS.design, 4), ...preHold('Write', ADAPTER_TEXTS.design, 5), turnEnd(6)])
  expect(lagSkip.nudges).toEqual({ design: { declined: 1 } })
  expect(nudgeRows(lagSkip)).toEqual([{ repeats: 3, skills: ['software-design-principles:declined'] }])
})

test('a repeat that no longer asks for what an earlier hold of its gate asked shows that ask met', async () => {
  // The second pipeline hold drops tdd with no load seen: the adapter judged it met, as a corrected route line does.
  const s = summarize([prompt(), ...preHold('Edit', ADAPTER_TEXTS.pipeline, 2), ...preHold('Edit', ADAPTER_TEXTS.pipeline.replace('`tdd`, ', ''), 3), turnEnd(4)])
  expect(s.nudges).toEqual({ pipeline: { followed: 1, unanswered: 1 } })
  expect(nudgeRows(s)).toEqual([{ repeats: 2, skills: ['tdd:followed', 'doc-sync:unanswered'] }])
})

// ---------- the design references: the design hold's reads, and the design-reads hold --------------------------------

const DESIGN_REFERENCES = '/skills/software-design-principles/references/'
const readTool = (path: string, t: number) => toolUseEvents([{ name: 'Read', input: { file_path: path } }], false, t)
const shellRead = (path: string, t: number) => toolUseEvents([{ name: 'Bash', input: { command: `cat ${path}` } }], false, t)

test('the design holds name the design skill only as a skip line, with the references they ask for', async () => {
  expect(hookName('design-reads')).toBe('design-reads hold')
  const skill = 'software-design-principles'
  expect(preHold('Edit', ADAPTER_TEXTS.designReads, 1)).toEqual([{ kind: 'nudge', t: 1, hook: 'design-reads', named: [skill], holdKind: 'justified-skip', skipOnly: [skill], refs: ['errors.md'] }])
  // Ticket 089: the design hold asks for the reads its edit selects and no design-reads line.
  expect(preHold('Write', ADAPTER_TEXTS.designFirstReads, 1)).toEqual([{ kind: 'nudge', t: 1, hook: 'design', named: [skill], holdKind: 'justified-skip', skipOnly: [skill], refs: ['process.md', 'complexity-and-modules.md', 'readability.md'] }])
})

test('the design-reads hold is followed only by a Read of each reference it names', async () => {
  const held = preHold('Edit', ADAPTER_TEXTS.designReads, 2)
  expect(summarize([prompt(), ...held, ...readTool(`${DESIGN_REFERENCES}errors.md`, 3), turnEnd(4)]).nudges).toEqual({ 'design-reads': { 'read files': 1 } })
  // A shell read, another reference, the red flags, or the skill's body is not the read it asks for.
  for (const other of [
    shellRead(`${DESIGN_REFERENCES}errors.md`, 3),
    readTool(`${DESIGN_REFERENCES}process.md`, 3),
    readTool(`${DESIGN_REFERENCES}red-flags.md`, 3),
    readTool('/skills/software-design-principles/SKILL.md', 3),
  ]) {
    expect(summarize([prompt(), ...held, ...other, turnEnd(4)]).nudges).toEqual({ 'design-reads': { unanswered: 1 } })
  }
  const reason = 'the edit only renames one local name'
  const declined = summarize([prompt(), ...held, ...markerEvents(`goated-skip: software-design-principles: ${reason}`, 3), turnEnd(4)])
  expect(declined.nudges).toEqual({ 'design-reads': { declined: 1 } })
  // Loading the skill again is not the read it asks for.
  expect(summarize([prompt(), ...held, load('software-design-principles', 3), turnEnd(4)]).nudges).toEqual({ 'design-reads': { unanswered: 1 } })
})

test('a design hold that asks for reads is followed only when every read is in; a design-reads line answers nothing', async () => {
  const line = markerEvents('goated-design-reads: none: only renames local names', 3)
  const held = preHold('Write', ADAPTER_TEXTS.designFirstReads, 2)
  const reads = (files: string[]) => files.flatMap((f, i) => readTool(`${DESIGN_REFERENCES}${f}`, 4 + i))
  const all = ['process.md', 'complexity-and-modules.md', 'readability.md']
  expect(summarize([prompt(), ...held, ...line, turnEnd(9)]).nudges).toEqual({ design: { unanswered: 1 } })
  expect(summarize([prompt(), ...held, ...line, ...reads(all.slice(1)), turnEnd(9)]).nudges).toEqual({ design: { unanswered: 1 } })
  expect(summarize([prompt(), ...held, ...reads(all), turnEnd(9)]).nudges).toEqual({ design: { 'read files': 1 } })
  // Nor does a design-reads line answer the design hold that asks for the load.
  expect(summarize([prompt(), ...preHold('Write', ADAPTER_TEXTS.design, 2), ...line, turnEnd(4)]).nudges).toEqual({ design: { unanswered: 1 } })
})

// ---------- the registry's skill references: the reference-reads hold (Ticket 067) ----------------------------------

const SKILL_REFERENCES = '/skills/'

test('the reference-reads hold names each skill only as a skip line, with the references it asks for', async () => {
  expect(hookName('reference-reads')).toBe('reference-reads hold')
  // Since Ticket 118 the hold comes from a short shell write (a ticket copied in after a check failed twice).
  expect(preHold('Bash', ADAPTER_TEXTS.referenceReads, 1)).toEqual([{
    kind: 'nudge', t: 1, hook: 'reference-reads', named: ['diagnose', 'spec-to-tickets'], holdKind: 'justified-skip',
    skipOnly: ['diagnose', 'spec-to-tickets'], refs: ['diagnose/references/root-cause-tracing.md', 'spec-to-tickets/references/ticket-slicing-templates.md'],
  }])
})

test('the reference-reads hold counts as read files only by a Read of each skill\'s own reference', async () => {
  const held = preHold('Bash', ADAPTER_TEXTS.referenceReads, 2)
  const tracing = readTool(`${SKILL_REFERENCES}diagnose/references/root-cause-tracing.md`, 3)
  const templates = readTool(`${SKILL_REFERENCES}spec-to-tickets/references/ticket-slicing-templates.md`, 4)
  expect(summarize([prompt(), ...held, ...tracing, ...templates, turnEnd(5)]).nudges).toEqual({ 'reference-reads': { 'read files': 2 } })
  expect(summarize([prompt(), ...held, ...tracing, turnEnd(5)]).nudges).toEqual({ 'reference-reads': { 'read files': 1, unanswered: 1 } })
  // A shell read, another skill's file of the same name, another reference, the skill's body, or a load is not the read.
  for (const other of [
    shellRead(`${SKILL_REFERENCES}diagnose/references/root-cause-tracing.md`, 3),
    readTool(`${SKILL_REFERENCES}spec-to-tickets/references/root-cause-tracing.md`, 3),
    readTool(`${SKILL_REFERENCES}diagnose/references/condition-based-waiting.md`, 3),
    readTool(`${SKILL_REFERENCES}diagnose/SKILL.md`, 3),
    [load('diagnose', 3)],
  ]) {
    expect(summarize([prompt(), ...held, ...other, turnEnd(5)]).nudges?.['reference-reads']?.['read files']).toBeUndefined()
  }
})

test('a skip line naming one skill declines only that skill\'s ask', async () => {
  const held = preHold('Bash', ADAPTER_TEXTS.referenceReads, 2)
  const reason = 'the failure names the wrong constant directly'
  const s = summarize([prompt(), ...held, ...markerEvents(`goated-skip: diagnose: ${reason}`, 3), turnEnd(4)])
  expect(s.nudges).toEqual({ 'reference-reads': { declined: 1, unanswered: 1 } })
  expect(s.skipReasons?.diagnose?.['reference-reads']).toBeDefined()
})

// ---------- joint holds: one message, every hold counted (Ticket 095) ----------------------------------

test('a message joining three holds counts each, as if shown alone', async () => {
  // Since Ticket 118 a short shell write meets the three: a settings file and a spec after a check failed twice.
  const held = preHold('Bash', ADAPTER_TEXTS.jointTestEdit, 2)
  expect(held.map(e => e.kind === 'nudge' && e.hook)).toEqual(['design-reads', 'reference-reads', 'repeated-failure'])
  const reason = 'the settings only copy the defaults'
  const s = summarize([
    prompt(), ...held,
    ...markerEvents(`goated-skip: software-design-principles: ${reason}`, 3),
    // A reference the hold did not name is not its read; the one it named is.
    ...readTool(`${SKILL_REFERENCES}spec-to-tickets/references/ticket-slicing-templates.md`, 4),
    ...readTool(`${SKILL_REFERENCES}write-a-spec/references/spec-template.md`, 5),
    load('diagnose', 6),
    turnEnd(7),
  ])
  expect(s.nudges).toEqual({ 'design-reads': { declined: 1 }, 'reference-reads': { 'read files': 1 }, 'repeated-failure': { followed: 1 } })
  // Near miss: with nothing done after it, each of the three is left unanswered.
  expect(summarize([prompt(), ...held, turnEnd(3)]).nudges).toEqual({
    'design-reads': { unanswered: 1 }, 'reference-reads': { unanswered: 1 }, 'repeated-failure': { unanswered: 1 },
  })
})

test('a short repeat names the same asks as its full hold', async () => {
  const shortHolds = preHold('Write', ADAPTER_TEXTS.securityShort, 1)
  const fullHolds = preHold('Write', ADAPTER_TEXTS.security, 1)
  expect(shortHolds[0]).toEqual(fullHolds[0])
  const items = (text: string) => stopHold(1, text).map(e => e.kind === 'nudge' && e.items)
  expect(items(ADAPTER_TEXTS.closeoutShort)).toEqual(items(ADAPTER_TEXTS.closeout))
})
