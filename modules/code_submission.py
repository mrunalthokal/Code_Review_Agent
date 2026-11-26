"""Module 1: Code Submission - paste / upload + syntax validation for Python & Java."""
import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

import javalang

from config import MAX_FILE_BYTES, SUPPORTED


@dataclass
class SyntaxIssue:
    line: int
    message: str


@dataclass
class Submission:
    filename: str
    language: str
    code: str
    valid: bool = False
    issues: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def detect_language(code: str, filename: str = "") -> str:
    ext = Path(filename).suffix.lower()
    if ext in SUPPORTED:
        return SUPPORTED[ext]
    if re.search(r"\b(public\s+class|import\s+java\.|System\.out)", code):
        return "java"
    return "python"


def _validate_python(code):
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return [SyntaxIssue(e.lineno or 0, e.msg)]


def _validate_java(code):
    try:
        javalang.parse.parse(code)
        return []
    except Exception as e:  # JavaSyntaxError, LexerError
        at = getattr(e, "at", None)
        pos = getattr(at, "position", at)
        line = pos[0] if isinstance(pos, (tuple, list)) else getattr(pos, "line", 0)
        return [SyntaxIssue(line or 0, getattr(e, "description", None) or str(e))]


def _metrics(code, language):
    lines = code.splitlines()
    comment = "#" if language == "python" else "//"
    return {
        "total_lines": len(lines),
        "blank_lines": sum(1 for l in lines if not l.strip()),
        "comment_lines": sum(1 for l in lines if l.strip().startswith(comment)),
        "characters": len(code),
    }


def process_submission(code: str, filename: str = "pasted_code", language: str = "") -> Submission:
    """Single entry point used by the UI and (later) the orchestrator."""
    language = language or detect_language(code, filename)
    sub = Submission(filename=filename, language=language, code=code)
    if not code.strip():
        sub.issues = [SyntaxIssue(0, "No code provided.")]
        return sub
    if len(code.encode("utf-8")) > MAX_FILE_BYTES:
        sub.issues = [SyntaxIssue(0, f"Code exceeds {MAX_FILE_BYTES // 1024} KB limit.")]
        return sub
    sub.issues = _validate_python(code) if language == "python" else _validate_java(code)
    sub.valid = not sub.issues
    sub.metrics = _metrics(code, language)
    return sub


def process_upload(filename: str, raw: bytes) -> Submission:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED:
        return Submission(filename, "unknown", "", False,
                          [SyntaxIssue(0, f"Unsupported file type '{ext}'. Use .py or .java")])
    try:
        code = raw.decode("utf-8")
    except UnicodeDecodeError:
        return Submission(filename, SUPPORTED[ext], "", False,
                          [SyntaxIssue(0, "File is not valid UTF-8 text.")])
    return process_submission(code, filename, SUPPORTED[ext])
