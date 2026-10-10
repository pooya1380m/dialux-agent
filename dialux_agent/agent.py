"""Tool-calling agent loop for any OpenAI-compatible chat API."""
from __future__ import annotations

import json
import os

from . import calc, compliance, knowledge, photometry

SYSTEM = ("You are a lighting design assistant for DIALux evo. Use the tools for numbers "
          "and knowledge; state that results are estimates to be verified in DIALux.")


def _luminaire(path: str) -> dict:
    l = photometry.load(path)
    return {**l.__dict__, "efficacy_lm_per_w": l.efficacy_lm_per_w}


def _check(room_type, em, u0, ugr=None, ra=None):
    v = compliance.check(room_type, em, u0, ugr, ra)
    return {"compliant": not v, "violations": v}


FUNCS = {
    "parse_photometry": _luminaire,
    "estimate_luminaires": calc.luminaires_needed,
    "check_compliance": _check,
    "search_knowledge": knowledge.search,
}


def _schema(name, desc, props, required):
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": {
        "type": "object", "properties": props, "required": required}}}


_num = {"type": "number"}
TOOL_SCHEMAS = [
    _schema("parse_photometry", "Read an LDT/IES file.", {"path": {"type": "string"}}, ["path"]),
    _schema("estimate_luminaires", "Lumen-method luminaire count.", {
        "target_lux": _num, "length": _num, "width": _num, "luminaire_flux_lm": _num,
        "height_above_workplane": _num, "maintenance_factor": _num},
        ["target_lux", "length", "width", "luminaire_flux_lm", "height_above_workplane"]),
    _schema("check_compliance", "Check results against EN 12464-1 targets.", {
        "room_type": {"type": "string"}, "em": _num, "u0": _num, "ugr": _num, "ra": _num},
        ["room_type", "em", "u0"]),
    _schema("search_knowledge", "Search DIALux/standards notes.", {
        "query": {"type": "string"}}, ["query"]),
]


def call_tool(name: str, arguments: dict):
    if name not in FUNCS:
        return {"error": f"unknown tool {name}"}
    try:
        if name == "parse_photometry":
            arguments = {"path": arguments["path"]}
        return FUNCS[name](**arguments)
    except Exception as e:  # report tool errors back to the model
        return {"error": str(e)}


def run(question: str, model: str | None = None, max_steps: int = 6) -> str:
    from openai import OpenAI  # optional dependency

    client = OpenAI()
    model = model or os.environ.get("DIALUX_AGENT_MODEL", "gpt-4o-mini")
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model=model, messages=msgs, tools=TOOL_SCHEMAS).choices[0].message
        msgs.append(msg)
        if not msg.tool_calls:
            return msg.content or ""
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = call_tool(tc.function.name, args)
            msgs.append({"role": "tool", "tool_call_id": tc.id,
                         "content": json.dumps(result, default=str)})
    return "Stopped: too many tool steps."
