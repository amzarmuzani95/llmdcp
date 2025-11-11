import docx
import pdfplumber
import streamlit as st
import tempfile

def read_docx(file) -> str:
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def read_pdf(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def download_txt(text: str, filename: str = "translated_file.txt"):
    return st.download_button(
        label = "Download as .txt",
        data = text,
        file_name = filename,
        mime="text/plain",
    )

def download_docx(text: str, filename: str = "translated_file.docx"):
    doc = docx.Document()
    for para in text.split("\n"):
        doc.add_paragraph(para)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        doc.save(tmp.name)
        with open(tmp.name, "rb") as f:
            data = f.read()
    return st.download_button(
        label = "Download as .docx",
        data = data,
        file_name = filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

def perplexity_check(text: str) -> float:
    """Return a crude "perplexity" estimate for the text using a trigram model.
    
    If the perplexity is too high (e.g. >1500), you may flag the translation for user review.
    """
    from collections import defaultdict
    import math
    
    words = text.split()
    trigram_counts = defaultdict(int)
    bigram_counts = defaultdict(int)
    unigram_counts = defaultdict(int)

    for i in range(len(words)):
        unigram_counts[words[i]] += 1
        if i >= 1:
            bigram_counts[(words[i-1], words[i])] += 1
        if i >= 2:
            trigram_counts[(words[i-2], words[i-1], words[i])] += 1

    V = len(unigram_counts)
    N = len(words)

    log_perp = 0.0
    for i in range(2, N):
        trigram = (words[i-2], words[i-1], words[i])
        bigram = (words[i-2], words[i-1])
        count_trigram = trigram_counts[trigram] + 1 # add-one smoothing
        count_bigram = bigram_counts[bigram] + V
        prob = count_trigram / count_bigram
        log_perp += -math.log(prob)

    return math.exp(log_perp / (N - 2))