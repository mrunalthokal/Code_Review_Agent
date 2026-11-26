"""Code Analysis Agent: code smells, complexity, anti-patterns, poor practices.
Python is analysed with the `ast` module, Java with `javalang` plus brace matching."""
import ast
import re

from agents.base import BaseAgent
from agents.llm_client import llm_review
from config import (MAX_CLASS_LINES, MAX_CLASS_METHODS, MAX_COMPLEXITY, MAX_FUNC_LINES,
                    MAX_LINE_LEN, MAX_NESTING, MAX_PARAMS)
from models import Finding, Severity

S = Severity
_NEST = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncFor, ast.AsyncWith)


def _py_complexity(fn):
    c = 1
    for n in ast.walk(fn):
        if isinstance(n, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.IfExp, ast.ExceptHandler)):
            c += 1
        elif isinstance(n, ast.BoolOp):
            c += len(n.values) - 1
        elif isinstance(n, ast.comprehension):
            c += 1 + len(n.ifs)
    return c


def _py_depth(node, depth=0):
    best = depth
    for child in ast.iter_child_nodes(node):
        is_elif = (isinstance(node, ast.If) and isinstance(child, ast.If)
                   and len(node.orelse) == 1 and node.orelse[0] is child)
        d = depth + 1 if isinstance(child, _NEST) and not is_elif else depth
        best = max(best, _py_depth(child, d))
    return best


def _strip_java(line):
    line = re.sub(r'"(\\.|[^"\\])*"', '""', line)
    return re.sub(r"//.*", "", line)


class CodeAnalysisAgent(BaseAgent):
    name = "Code Analysis Agent"

    def analyze(self, sub):
        self.lines = sub.code.splitlines()
        out = self._python(sub.code) if sub.language == "python" else self._java(sub.code)
        out += self._common()
        if self.use_llm:
            extra, note = llm_review(self.name, "code quality and design", sub, out)
            self.notes.append(note)
            out += extra
        return out

    # ---------- helpers ----------
    def _f(self, rule_id, title, category, sev, line, desc, rec):
        snip = self.lines[line - 1].strip()[:160] if 1 <= line <= len(self.lines) else ""
        return Finding(self.name, rule_id, title, category, sev, line, desc, rec, snip)

    def _find_line(self, pattern, start=1):
        rx = re.compile(pattern)
        for i in range(start - 1, len(self.lines)):
            if rx.search(self.lines[i]):
                return i + 1
        return 1

    # ---------- Python ----------
    def _python(self, code):
        out = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return out
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out += self._py_function(n)
            elif isinstance(n, ast.ClassDef):
                methods = [m for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                length = n.end_lineno - n.lineno + 1
                if len(methods) > MAX_CLASS_METHODS or length > MAX_CLASS_LINES:
                    out.append(self._f("CA-CLASS", "Large Class (God Class)", "Design", S.MEDIUM, n.lineno,
                        f"Class '{n.name}' has {len(methods)} methods and {length} lines.",
                        "Split by responsibility (Single Responsibility Principle)."))
            elif isinstance(n, ast.ExceptHandler):
                if n.type is None:
                    out.append(self._f("CA-BARE", "Bare except", "Error Handling", S.MEDIUM, n.lineno,
                        "A bare 'except:' also catches SystemExit and KeyboardInterrupt and hides bugs.",
                        "Catch specific exceptions and log them."))
                elif all(isinstance(s, ast.Pass) for s in n.body):
                    out.append(self._f("CA-SWALLOW", "Swallowed exception", "Error Handling", S.MEDIUM, n.lineno,
                        "Exception is caught and silently ignored.", "Handle or at least log the error."))
            elif isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names):
                out.append(self._f("CA-WILDCARD", "Wildcard import", "Style", S.LOW, n.lineno,
                    "'import *' pollutes the namespace and hides where names come from.",
                    "Import only the names you need."))
            elif isinstance(n, ast.Global):
                out.append(self._f("CA-GLOBAL", "Use of global state", "Design", S.LOW, n.lineno,
                    "Global variables make code hard to test and reason about.",
                    "Pass values as parameters or use a class."))
        used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        for n in ast.walk(tree):
            if isinstance(n, (ast.Import, ast.ImportFrom)) and getattr(n, "module", "") != "__future__":
                for a in n.names:
                    name = (a.asname or a.name).split(".")[0]
                    if name != "*" and name not in used:
                        out.append(self._f("CA-UNUSED-IMPORT", "Unused import", "Dead Code", S.LOW, n.lineno,
                            f"'{name}' is imported but never used.", "Remove the unused import."))
        return out

    def _py_function(self, fn):
        out, a = [], fn.args
        length = fn.end_lineno - fn.lineno + 1
        if length > 80 or length > MAX_FUNC_LINES:
            out.append(self._f("CA-LONG-METHOD", "Long Method", "Maintainability",
                S.MEDIUM if length > 80 else S.LOW, fn.lineno,
                f"Function '{fn.name}' is {length} lines (limit {MAX_FUNC_LINES}).",
                "Apply Extract Method so each function does one thing."))
        params = [p.arg for p in a.posonlyargs + a.args + a.kwonlyargs if p.arg not in ("self", "cls")]
        if len(params) > MAX_PARAMS:
            out.append(self._f("CA-PARAMS", "Too Many Parameters", "Design",
                S.MEDIUM if len(params) > 8 else S.LOW, fn.lineno,
                f"'{fn.name}' takes {len(params)} parameters (limit {MAX_PARAMS}).",
                "Group related parameters into a dataclass/object."))
        cx = _py_complexity(fn)
        if cx > MAX_COMPLEXITY:
            out.append(self._f("CA-COMPLEXITY", "High Cyclomatic Complexity", "Complexity",
                S.HIGH if cx > 20 else S.MEDIUM, fn.lineno,
                f"'{fn.name}' has cyclomatic complexity {cx} (limit {MAX_COMPLEXITY}).",
                "Use guard clauses, split into smaller functions, or replace branches with lookup tables."))
        depth = _py_depth(fn)
        if depth > MAX_NESTING:
            out.append(self._f("CA-NESTING", "Deep Nesting", "Complexity", S.MEDIUM, fn.lineno,
                f"'{fn.name}' nests blocks {depth} levels deep (limit {MAX_NESTING}).",
                "Return early and extract inner blocks into helpers."))
        defaults = list(a.defaults) + [d for d in a.kw_defaults if d is not None]
        if any(isinstance(d, (ast.List, ast.Dict, ast.Set)) for d in defaults):
            out.append(self._f("CA-MUTABLE-DEFAULT", "Mutable default argument", "Bug Risk", S.MEDIUM, fn.lineno,
                f"'{fn.name}' uses a mutable default; it is shared between calls.",
                "Use None as default and create the object inside the function."))
        if length > 15 and not fn.name.startswith("_") and not ast.get_docstring(fn):
            out.append(self._f("CA-DOCSTRING", "Missing docstring", "Documentation", S.INFO, fn.lineno,
                f"Public function '{fn.name}' has no docstring.", "Document purpose, parameters and return value."))
        return out

    # ---------- Java ----------
    def _java(self, code):
        import javalang
        out = []
        try:
            tree = javalang.parse.parse(code)
        except Exception:
            return out
        T = javalang.tree
        for _, m in list(tree.filter(T.MethodDeclaration)) + list(tree.filter(T.ConstructorDeclaration)):
            out += self._java_method(m, T)
        for _, c in tree.filter(T.ClassDeclaration):
            start = self._pos(c) or self._find_line(rf"\bclass\s+{c.name}\b")
            length = self._block_end(start) - start + 1
            n_methods = len(c.methods)
            if n_methods > MAX_CLASS_METHODS or length > MAX_CLASS_LINES:
                out.append(self._f("CA-CLASS", "Large Class (God Class)", "Design", S.MEDIUM, start,
                    f"Class '{c.name}' has {n_methods} methods and ~{length} lines.",
                    "Split by responsibility (Single Responsibility Principle)."))
            if not re.match(r"^[A-Z][A-Za-z0-9]*$", c.name):
                out.append(self._f("CA-NAMING", "Naming convention", "Style", S.LOW, start,
                    f"Class '{c.name}' should be PascalCase.", "Rename following Java conventions."))
        body = "\n".join(l for l in self.lines if not l.strip().startswith("import "))
        for imp in tree.imports:
            short = imp.path.split(".")[-1]
            if imp.wildcard or imp.static:
                continue
            if not re.search(rf"\b{re.escape(short)}\b", body):
                out.append(self._f("CA-UNUSED-IMPORT", "Unused import", "Dead Code", S.LOW,
                    self._find_line(rf"^\s*import\s+{re.escape(imp.path)}\s*;"),
                    f"'{short}' is imported but never used.", "Remove the unused import."))
        for m in re.finditer(r"catch\s*\([^)]*\)\s*\{\s*\}", code):
            out.append(self._f("CA-SWALLOW", "Empty catch block", "Error Handling", S.MEDIUM,
                code[:m.start()].count("\n") + 1, "Exception is caught and silently ignored.",
                "Handle or log the exception."))
        for m in re.finditer(r"catch\s*\(\s*(Exception|Throwable)\s+\w+\s*\)", code):
            out.append(self._f("CA-GENERIC-CATCH", "Overly broad catch", "Error Handling", S.LOW,
                code[:m.start()].count("\n") + 1, f"Catching {m.group(1)} hides unrelated failures.",
                "Catch the specific exception types you can handle."))
        return out

    def _pos(self, node):
        pos = getattr(node, "position", None)
        if pos:
            return pos[0] if isinstance(pos, (tuple, list)) else getattr(pos, "line", None)
        return None

    def _block_end(self, start):
        depth, seen = 0, False
        for i in range(start - 1, len(self.lines)):
            for ch in _strip_java(self.lines[i]):
                if ch == "{":
                    depth, seen = depth + 1, True
                elif ch == "}":
                    depth -= 1
            if seen and depth <= 0:
                return i + 1
        return len(self.lines)

    def _java_method(self, m, T):
        out = []
        start = self._pos(m) or self._find_line(rf"\b{re.escape(m.name)}\s*\([^;]*$")
        end = self._block_end(start)
        length = end - start + 1
        if length > MAX_FUNC_LINES:
            out.append(self._f("CA-LONG-METHOD", "Long Method", "Maintainability",
                S.MEDIUM if length > 80 else S.LOW, start,
                f"Method '{m.name}' is ~{length} lines (limit {MAX_FUNC_LINES}).",
                "Apply Extract Method so each method does one thing."))
        n_params = len(m.parameters)
        if n_params > MAX_PARAMS:
            out.append(self._f("CA-PARAMS", "Too Many Parameters", "Design",
                S.MEDIUM if n_params > 8 else S.LOW, start,
                f"'{m.name}' takes {n_params} parameters (limit {MAX_PARAMS}).",
                "Group related parameters into an object (parameter object / builder)."))
        cx = 1
        for t in (T.IfStatement, T.ForStatement, T.WhileStatement, T.DoStatement,
                  T.SwitchStatementCase, T.CatchClause, T.TernaryExpression):
            cx += sum(1 for _ in m.filter(t))
        cx += sum(1 for _, b in m.filter(T.BinaryOperation) if b.operator in ("&&", "||"))
        if cx > MAX_COMPLEXITY:
            out.append(self._f("CA-COMPLEXITY", "High Cyclomatic Complexity", "Complexity",
                S.HIGH if cx > 20 else S.MEDIUM, start,
                f"'{m.name}' has cyclomatic complexity {cx} (limit {MAX_COMPLEXITY}).",
                "Use guard clauses, extract methods, or replace conditionals with polymorphism."))
        depth = mx = 0
        for i in range(start - 1, min(end, len(self.lines))):
            for ch in _strip_java(self.lines[i]):
                if ch == "{":
                    depth += 1
                    mx = max(mx, depth)
                elif ch == "}":
                    depth -= 1
        if mx - 1 > MAX_NESTING:
            out.append(self._f("CA-NESTING", "Deep Nesting", "Complexity", S.MEDIUM, start,
                f"'{m.name}' nests blocks {mx - 1} levels deep (limit {MAX_NESTING}).",
                "Return early and extract inner blocks into helper methods."))
        if isinstance(m, T.MethodDeclaration) and not re.match(r"^[a-z][A-Za-z0-9]*$", m.name):
            out.append(self._f("CA-NAMING", "Naming convention", "Style", S.LOW, start,
                f"Method '{m.name}' should be camelCase.", "Rename following Java conventions."))
        return out

    # ---------- both languages ----------
    def _common(self):
        out = []
        long_lines = [i for i, l in enumerate(self.lines, 1) if len(l) > MAX_LINE_LEN]
        if long_lines:
            out.append(self._f("CA-LINE-LEN", "Overly long lines", "Style", S.LOW, long_lines[0],
                f"{len(long_lines)} line(s) exceed {MAX_LINE_LEN} characters (first shown).",
                "Wrap or refactor long expressions."))
        todos = [i for i, l in enumerate(self.lines, 1) if re.search(r"\b(TODO|FIXME|HACK)\b", l)]
        if todos:
            out.append(self._f("CA-TODO", "Unresolved TODO/FIXME", "Maintainability", S.INFO, todos[0],
                f"{len(todos)} TODO/FIXME marker(s) found (first shown).", "Resolve or track them in an issue."))
        return out
