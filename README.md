# dialux-agent

Python tools for an AI agent that assists with DIALux evo lighting design.
DIALux evo has no public API, so this works on exchange files and calculations.

- `photometry.py` – parse LDT (Eulumdat) / IES files: flux, power, efficacy
- `calc.py` – lumen-method luminaire count estimate (approximate utilance)
- `compliance.py` – subset of EN 12464-1 targets (verify against the standard)
- `knowledge.py` + `knowledge/` – keyword search over notes (add your own .md/.txt files)
- `agent.py` – tool-calling loop for OpenAI-compatible APIs (`pip install openai`, set `OPENAI_API_KEY`)
- `ui_driver.py` – optional pywinauto launcher (Windows only)
- `cli.py` – CLI; `TOOLS` dict can be registered with any tool-calling LLM

```
python -m dialux_agent.cli parse luminaire.ldt
python -m dialux_agent.cli estimate --lux 500 --length 6 --width 5 --height 2 --flux 4000
python -m dialux_agent.cli check office --em 520 --u0 0.65
python -m dialux_agent.cli kb "emergency lighting"
python -m dialux_agent.cli ask "How many luminaires for a 6x5 m office?"
python -m pytest
```

Estimates are pre-calculations; validate against DIALux results.
Not implemented: embedding-based RAG, C# plugin bridge (needs DIAL's SDK), validation against real DIALux projects.
# dialux-agent
