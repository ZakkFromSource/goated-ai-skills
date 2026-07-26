# Merge Conflict Fixtures

These fixtures exercise intent-preserving resolution of active Git merges,
rebases, cherry-picks, and reverts.

They validate portable outcomes rather than shell syntax:

- detect the active operation and exact unmerged scope before editing;
- trace both sides to primary intent evidence;
- preserve compatible intent without inventing unrelated behavior;
- stop for an explicit decision when intent is incompatible;
- allow safe abort when evidence or operation state makes continuation unsafe;
- discover checks scoped to the resolution; and
- keep stage, commit, continue, abort, push, and protected-branch authority
  outside the skill in standalone and integrated use.
