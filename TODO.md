# Aevor AI TODO

## Completed

- [x] Clone and inspect repository
- [x] Create initial AGENTS.md
- [x] Create TODO.md
- [x] Define Phase 1 service architecture
- [x] Define Python/FastAPI project structure
- [x] Define configuration approach
- [x] Define logging approach
- [x] Implement health endpoint
- [x] Implement readiness endpoint
- [x] Add initial tests
- [x] Define actual AI functionality (Git Diff Summarizer / PR Description Generator)
- [x] Select appropriate model (gemini-2.5-flash)
- [x] Create provider-independent model abstraction interface
- [x] Implement Gemini API provider integration
- [x] Add automated unit tests for model provider layer

## Currently Working On

- None

## Blocked

- None

## Next

- [ ] Implement diff summarizer logic (prompts and service pipeline)
- [ ] Expose `/summarize-diff` endpoint in API layer

## Future

- [ ] Add Docker configuration
- [ ] Add CI setup
- [ ] Integrate with Aevor Platform
- [ ] Evaluate model performance/hallucinations

## Notes

- Aevor AI is an independent microservice.
- Do not move AI implementation into Aevor Platform.
- Do not select an LLM before the actual AI functionality is defined.
- Work on one task at a time.
- Do not mark work complete without verification.
