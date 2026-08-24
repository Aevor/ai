\# Aevor AI Agent Instructions



\## Repository Purpose



Aevor AI is an independent AI microservice within the Aevor platform.



The service is responsible for AI/ML capabilities and must remain independently maintainable and deployable.



\## Architecture



Aevor AI communicates with the Aevor Platform through a defined service API.



The platform must not directly access:

\- AI model internals

\- model files

\- preprocessing internals

\- inference implementation



Preferred architecture:



Platform

&#x20;   |

&#x20;   | HTTP / Internal API

&#x20;   v

Aevor AI

&#x20;   |

&#x20;   v

AI Service Layer

&#x20;   |

&#x20;   v

Inference Layer

&#x20;   |

&#x20;   v

Model



\## Agent Workflow



Before starting any task:



1\. Read AGENTS.md.

2\. Read TODO.md.

3\. Inspect the existing implementation.

4\. Identify the next unfinished task.

5\. Implement only that task.

6\. Run relevant tests.

7\. Update TODO.md.

8\. Update AGENTS.md if architecture or development rules changed.

9\. Report the work clearly.



Do not randomly implement future features.



\## Development Rules



\- Preserve existing architecture unless there is a clear technical reason to change it.

\- Keep the AI service independent from Aevor Platform.

\- Do not modify unrelated repositories.

\- Do not add unnecessary dependencies.

\- Do not commit secrets or credentials.

\- Do not commit API keys, passwords, tokens, or private keys.

\- Do not commit large model files unless explicitly required.

\- Validate external input.

\- Do not expose raw stack traces through APIs.

\- Test meaningful functionality.

\- Do not claim work is complete without verification.



\## Git Workflow



Use feature branches.



Examples:



\- feat/...

\- fix/...

\- refactor/...

\- test/...

\- docs/...

\- chore/...



Keep commits focused and meaningful.



\## Current Development Principle



Prioritize:



1\. Correctness

2\. Testing

3\. Documentation

4\. Containerization

5\. Integration

6\. Measurement

7\. Optimization



Do not introduce complex infrastructure without a demonstrated requirement.



\## AI Model Selection



Do not select or integrate an AI model until the actual AI functionality and requirements have been defined.



Model selection must consider:

\- purpose

\- input

\- output

\- license

\- resource requirements

\- latency

\- limitations



\## Completion Report



Every AI coding-agent task should report:



1\. What was implemented

2\. Files changed

3\. Tests executed

4\. Test results

5\. TODO status

6\. Remaining work

7\. Blockers

8\. Architectural concerns

