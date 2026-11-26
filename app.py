import json

import streamlit as st

from agents.orchestrator import run_review
from config import GEMINI_API_KEY, TOP_K
from models import SEVERITY_ICON
from modules.code_submission import process_submission, process_upload
from rag.pipeline import build_index, get_store
from validation.run_validation import run_validation, to_markdown

st.set_page_config(page_title="AI Code Review & Security Agent", page_icon="🛡️", layout="wide")
st.title("🛡️ Smart Code Inspection Platform")
st.caption("Milestone 1: Submission + RAG Knowledge Base  |  Milestone 2: Multi-Agent Analysis")
st.sidebar.info(f"Gemini key: **{'found' if GEMINI_API_KEY else 'not set (static rules only)'}**")

tab1, tab2, tab3, tab4 = st.tabs(["📥 Code Submission", "🔍 Multi-Agent Analysis", "📚 Knowledge Base & RAG",
                                  "✅ Accuracy Validation"])

# ---------------- Tab 1: submission ----------------
with tab1:
    mode = st.radio("Input method", ["Paste code", "Upload file"], horizontal=True)
    sub = None
    if mode == "Paste code":
        lang = st.selectbox("Language", ["python", "java"])
        code = st.text_area("Paste your code", height=300)
        if st.button("Validate & Submit", type="primary"):
            sub = process_submission(code, "pasted_code", lang)
    else:
        up = st.file_uploader("Upload .py or .java", type=["py", "java"])
        if up and st.button("Validate & Submit", type="primary"):
            sub = process_upload(up.name, up.read())
    if sub:
        if sub.valid:
            st.success(f"✅ Valid {sub.language.title()} code. Go to the 'Multi-Agent Analysis' tab.")
            st.json(sub.metrics)
            st.code(sub.code, language=sub.language, line_numbers=True)
            st.session_state["submission"] = sub
            st.session_state.pop("review", None)
        else:
            for i in sub.issues:
                st.error(f"Line {i.line}: {i.message}" if i.line else i.message)

# ---------------- Tab 2: analysis ----------------
with tab2:
    sub = st.session_state.get("submission")
    if not sub:
        st.info("Submit valid code in the first tab.")
    else:
        st.write(f"**File:** {sub.filename}  |  **Language:** {sub.language}")
        use_llm = st.checkbox("Augment with Gemini AI review", disabled=not GEMINI_API_KEY,
                              help="Adds AI-found issues on top of the static rules. Needs GEMINI_API_KEY in .env")
        if st.button("▶ Run Multi-Agent Analysis", type="primary"):
            with st.spinner("Code Analysis + Security agents running in parallel..."):
                st.session_state["review"] = run_review(sub, use_llm)
        rev = st.session_state.get("review")
        if rev:
            s = rev.summary
            c = st.columns(6)
            c[0].metric("Total findings", s["total"])
            for col, sev in zip(c[1:5], ["Critical", "High", "Medium", "Low"]):
                col.metric(f"{SEVERITY_ICON[sev]} {sev}", s["by_severity"][sev])
            c[5].metric("Health score", f"{s['health_score']}/100")

            st.subheader("Agent execution (parallel)")
            st.dataframe([{"Agent": k, "Status": v["status"], "Findings": v["findings"],
                           "Seconds": v["seconds"], "Notes": "; ".join(v["notes"]) or v["error"]}
                          for k, v in rev.agent_runs.items()], use_container_width=True, hide_index=True)

            st.subheader("Unified findings")
            f1, f2 = st.columns(2)
            sev_sel = f1.multiselect("Severity", list(s["by_severity"]), default=list(s["by_severity"]))
            ag_sel = f2.multiselect("Agent", list(rev.agent_runs), default=list(rev.agent_runs))
            for f in rev.findings:
                if f.severity.value not in sev_sel or f.agent not in ag_sel:
                    continue
                with st.expander(f"{SEVERITY_ICON[f.severity.value]} {f.id} [{f.severity.value}] "
                                 f"{f.title}: line {f.line}"):
                    st.write(f.description)
                    st.code(f"{f.line}: {f.snippet}", language=sub.language)
                    st.markdown(f"**Recommendation:** {f.recommendation}")
                    st.caption(f"{f.agent}  |  {f.category}  |  score {f.score}"
                               + (f"  |  {f.owasp}" if f.owasp else "") + (f"  |  {f.cwe}" if f.cwe else "")
                               + f"  |  source: {f.source}")
            st.download_button("⬇ Download findings (JSON)", json.dumps(rev.to_dict(), indent=2),
                               file_name="findings.json", mime="application/json")

# ---------------- Tab 3: knowledge base ----------------
with tab3:
    if st.button("🔨 Build / Rebuild Index"):
        with st.spinner("Chunking, embedding, indexing..."):
            st.success(build_index())
    st.divider()
    q = st.text_input("Test retrieval", placeholder="How do I prevent SQL injection in Java?")
    if q:
        try:
            hits = get_store().search(q, TOP_K)
            if not hits:
                st.warning("Index is empty. Click 'Build / Rebuild Index' first.")
            for h in hits:
                with st.expander(f"{h['source']} › {h['section']}  (score {h['score']})"):
                    st.write(h["text"])
        except Exception as e:
            st.warning(f"Build the index first. ({e})")

# ---------------- Tab 4: accuracy validation ----------------
with tab4:
    st.write("Runs both agents on labeled sample files in `validation/samples/` (Python and Java, "
             "known issues marked with `EXPECT:` comments) and measures detection accuracy.")
    if st.button("▶ Run Validation", type="primary"):
        with st.spinner("Analysing sample codebases..."):
            st.session_state["validation"] = run_validation(False)
    v = st.session_state.get("validation")
    if v:
        for w in v["warnings"]:
            st.warning(w)
        allrow = next(m for m in v["metrics"] if m["language"] == "all" and m["agent"] == "all")
        c = st.columns(4)
        c[0].metric("Precision", f"{(allrow['precision'] or 0) * 100:.1f}%")
        c[1].metric("Recall", f"{(allrow['recall'] or 0) * 100:.1f}%")
        c[2].metric("F1 score", f"{(allrow['f1'] or 0) * 100:.1f}%")
        c[3].metric("TP / FP / FN", f"{allrow['tp']} / {allrow['fp']} / {allrow['fn']}")
        st.subheader("Per agent and language")
        st.dataframe(v["metrics"], use_container_width=True, hide_index=True)
        st.subheader("Per sample file")
        st.dataframe(v["files"], use_container_width=True, hide_index=True)
        st.subheader("Per issue type")
        st.dataframe(v["by_title"], use_container_width=True, hide_index=True)
        st.subheader("Missed issues (false negatives)")
        st.dataframe(v["missed"] or [{"result": "none"}], use_container_width=True, hide_index=True)
        st.subheader("False alarms (false positives)")
        st.dataframe(v["false_positives"] or [{"result": "none"}], use_container_width=True, hide_index=True)
        st.download_button("⬇ Download report (Markdown)", to_markdown(v), file_name="validation_report.md")
