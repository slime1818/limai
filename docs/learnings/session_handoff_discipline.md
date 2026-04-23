# Session handoff discipline

## Lesson
Multi-day agentic coding projecten vereisen expliciete context-handoff docs. Memory tussen sessies is niet betrouwbaar, Claude Code context reset elke chat, userMemories kunnen out-of-date zijn. De enige stabiele context is: git commits met sprekende messages + status docs in versioned repo.

## Validation
- `docs/status/YYYY-MM-DD-[topic].md` pattern used throughout 6 biomes. Elke chat-start begon met "read docs/DESIGN.md + recent commits + docs/status/[latest].md" en dat werkte consistent.
- Pacifico boats architecture bug (my error): baked boats into plateau prompt v1. User caught it correctly because architecture was documented in status docs — could cross-reference against "boats must parallax" requirement.
- Premature Pacifico production-lock (my error on commit 28a892a): followed by visual-verify catch of pink-hulls regression. Git history preserved both the bad commit and the c9fce42 fix as engineering evidence.

## Pattern
End of every session (chat or work block):
1. Status doc naar `docs/status/YYYY-MM-DD-[topic].md`:
   - Current state (what's locked, what's WIP)
   - Immediate next step (exact command or decision needed)
   - Context pointers (which docs/DESIGN.md sections relevant, which commits)
   - Budget remaining if relevant
2. Git commit atomic met sprekende message — include regression or failure modes in commit message ("v2 abandoned because X, v3 succeeded because Y")
3. Never wrap to next session without commit. In-memory state is never recoverable.

Start of every session:
1. `git status` → verify clean
2. `git pull origin main` → verify sync
3. Read latest docs/status/ file for resume point
4. Read referenced docs/DESIGN.md sections
5. Proceed from documented resume-point, never from memory alone

## Anti-pattern
Deze warning is belangrijk: Claude's memory (userMemories) kan verouderd zijn. Tijdens Pacifico had ik memory "project folder = agency-site" terwijl werkelijke folder al maanden "projects/limai" was. Status docs + git zijn source of truth, memory is hint.
