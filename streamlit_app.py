from altair import BaseTitleNoValueRefs
import streamlit as st
import os
import tempfile
import copy
from pathlib import Path
from src.sap_reader import SAPReader
from src.extractor import Extractor
from src.mockshell_generator import MockShellGenerator
from src.exporter import Exporter

st.set_page_config(page_title="Universal Domain MockShell Generator", page_icon="🔬", layout="wide")

# CSS Presentation layer styling templates - OPTIMIZED FOR LIGHT THEME
st.markdown("""
<style>
    /* Main Background & Text Setup */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
    }

    /* Professional Soft Light Header Container */
    .header-container {
        background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
        padding: 2.5rem 2rem;
        border-radius: 12px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
    }
    
    .header-container h1 {
        color: #ffffff !important;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-container p {
        color: #ccfbf1 !important;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Content Cards Container */
    .content-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    }

    /* MockShell Preview Box */
    .shell-preview {
        background-color: #f1f5f9;
        color: #0f172a;
        font-family: 'Consolas', 'Courier New', monospace;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        white-space: pre-wrap;
        overflow-x: auto;
        font-size: 13px;
        line-height: 1.6;
    }

    /* Raw Text Preview Box */
    .text-preview {
        background-color: #f8fafc;
        color: #334155;
        font-family: 'Consolas', 'Courier New', monospace;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        max-height: 350px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-size: 13px;
    }

    /* Force Streamlit Select Widgets to match light theme cleanly */
    div[data-baseweb="select"] {
        background-color: #ffffff !important;
    }
</style>

<div class="header-container">
    <h1>Universal Domain MockShell Generator</h1>
    <p>Disposition & Clinical Laboratory Spec Sheet Validation Portal</p>
</div>
""", unsafe_allow_html=True)

if 'templates' not in st.session_state: st.session_state.templates = None
if 'processed_filename' not in st.session_state: st.session_state.processed_filename = None
if 'extracted_raw_text' not in st.session_state: st.session_state.extracted_raw_text = ""

st.markdown('<div class="content-card">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 1, 1])
with c1: uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx"], label_visibility="collapsed")
with c2: 
    export_format = st.selectbox(
        "Format Output Selection", 
        ["PDF Document (.pdf)", "Word Document (.docx)", "Excel Workbook (.xlsx)", "Markdown Specification (.md)"], 
        label_visibility="collapsed"
    )
with c3: generate_clicked = st.button("Generate Layout Shells", disabled=(uploaded_file is None), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file and generate_clicked:
    with st.spinner("Processing pipeline sequence..."):
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                temp_path = Path(tmp_dir) / uploaded_file.name
                with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                
                raw_text = SAPReader(str(temp_path)).read()
                st.session_state.extracted_raw_text = raw_text
                
                tlfs = Extractor(raw_text).extract_tlfs()
                st.session_state.templates = MockShellGenerator(tlfs).generate_templates()
                st.session_state.processed_filename = uploaded_file.name
        except Exception as e:
            st.error(f"Pipeline failure: {str(e)}")

if st.session_state.templates:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    exporter = Exporter(tempfile.gettempdir())
    out_stem = Path(st.session_state.processed_filename).stem

    if "PDF" in export_format:
        out_name = f"MockShells_{Path(st.session_state.processed_filename).stem}.pdf"
        file_path = exporter.export_to_pdf(st.session_state.templates, filename=out_name)
        mime = "application/pdf"
        btn_txt = "📥 Export PDF Report (.pdf)"
    elif "Word" in export_format:
        out_name = f"MockShells_{Path(st.session_state.processed_filename).stem}.docx"
        file_path = exporter.export_to_word(st.session_state.templates, filename=out_name)
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        btn_txt = "📥 Export Word Document (.docx)"
    elif "Excel" in export_format:
        out_name = f"MockShells_{Path(st.session_state.processed_filename).stem}.xlsx"
        file_path = exporter.export_to_excel(st.session_state.templates, filename=out_name)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        btn_txt = "📥 Export Excel Workbook (.xlsx)"
    else:
        out_name = f"MockShells_{Path(st.session_state.processed_filename).stem}.md"
        file_path = exporter.export_to_md(st.session_state.templates, filename=out_name)
        mime = "text/markdown"
        btn_txt = "📥 Export Markdown Specification (.md)"

    pc1, pc2 = st.columns([3, 1])
    with pc1:
        titles = [f"[{t.get('category')}] {t.get('type')} {t.get('number')}: {t.get('title')}" for t in st.session_state.templates]
        selected_idx = st.selectbox("Select target schema:", range(len(titles)), format_func=lambda x: titles[x])
    with pc2:
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f: 
                st.download_button(
                     label=btn_txt, 
                     data=f.read(), 
                     file_name=out_name, 
                     mime=mime,
                     use_container_width=True
               )

    tab_preview, tab_metadata, tab_raw = st.tabs(["🖥️ Layout Render View", "🧠 LLaMA Metadata Schema", "📄 Extracted Raw Source"])
    
    with tab_preview:
        shell = st.session_state.templates[selected_idx]
        lines = [f"Domain: {shell.get('category','').upper()}", f"{shell.get('type')} {shell.get('number')} : {shell.get('title')}", "═"*80, f"Population: {shell.get('population','')}", "─"*80]
        hdrs, rows = shell.get('headers', []), shell.get('rows', [])
        if hdrs:
            col_w = [30 if idx == 0 else 16 for idx in range(len(hdrs))]
            lines.append("".join(str(h).replace('\n', ' ').ljust(col_w[idx]) if idx == 0 else str(h).replace('\n', ' ').center(col_w[idx]) for idx, h in enumerate(hdrs)))
            lines.append("-" * sum(col_w))
            for r in rows:
                lines.append("".join(str(val)[:col_w[idx]].ljust(col_w[idx]) if idx == 0 else str(val)[:col_w[idx]].center(col_w[idx]) for idx, val in enumerate(r) if idx < len(hdrs)))
        lines.extend(["═"*80, shell.get('notes_section', ''), shell.get('prog_notes', '')])
        st.markdown(f'<div class="shell-preview">{"<br>".join(lines)}</div>', unsafe_allow_html=True)

    with tab_metadata: st.json(st.session_state.templates[selected_idx])
    with tab_raw: st.markdown(f'<div class="text-preview">{st.session_state.extracted_raw_text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)