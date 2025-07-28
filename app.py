import fitz  # PyMuPDF
import re
import json
import os
from difflib import SequenceMatcher

# --------------------------
# 1) Extract TOC if available (Best Accuracy)
# --------------------------
def extract_toc(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc(simple=True)  # [(level, title, page)]
    if not toc:
        return None

    outline = []
    for level, text, page in toc:
        level_tag = f"H{level}" if level <= 4 else "H4"
        outline.append({
            "level": level_tag,
            "text": text.strip(),
            "page": page
        })
    return outline

# --------------------------
# 2) Improved regex-based heading detection (Fallback)
# --------------------------
def regex_heading_detection(text, page_num, seen_headings):
    headings = []
    numbered = re.compile(r"^(\d+(\.\d+)*)(\s+)(.+)$")
    keywords = ["summary", "background", "timeline", "introduction", "conclusion",
                "acknowledgements", "references", "appendix"]

    for line in text.split("\n"):
        line_clean = line.strip()
        if not line_clean:
            continue

        # Strict filter: skip long sentences (>8 words)
        if len(line_clean.split()) > 8:
            continue

        # Avoid duplicates
        if line_clean.lower() in seen_headings:
            continue

        # --- Numbered headings ---
        match = numbered.match(line_clean)
        if match:
            numbering = match.group(1)
            heading_text = match.group(4).strip()
            level = numbering.count(".") + 1
            level_tag = f"H{level}" if level <= 4 else "H4"
            seen_headings.add(line_clean.lower())
            headings.append({
                "level": level_tag,
                "text": heading_text,
                "page": page_num
            })

        # --- Heuristic non-numbered headings ---
        elif (line_clean.lower().strip(":") in keywords or
              line_clean.endswith(":") or
              (line_clean.istitle() and 2 <= len(line_clean.split()) <= 6)):
            seen_headings.add(line_clean.lower())
            headings.append({
                "level": "H2",
                "text": line_clean,
                "page": page_num
            })

    return headings

# --------------------------
# 3) Better Title Extraction
# --------------------------
def extract_title(doc, outline=None):
    meta_title = doc.metadata.get("title")
    if meta_title and meta_title.strip():
        return meta_title.strip()

    # If TOC exists, first H1 can be used as title
    if outline:
        for item in outline:
            if item["level"] == "H1":
                return item["text"]

    # Fallback: largest block on first page
    page1 = doc[0]
    blocks = page1.get_text("blocks")
    if not blocks:
        return os.path.basename(doc.name)
    largest_block = max(blocks, key=lambda b: b[3] - b[1])
    return largest_block[4].strip() if largest_block[4].strip() else os.path.basename(doc.name)

# --------------------------
# 4) Process PDF (TOC + Fallback)
# --------------------------
def process_pdf(pdf_path):
    print(f"Processing {pdf_path}...")
    doc = fitz.open(pdf_path)

    toc_outline = extract_toc(pdf_path)
    title = extract_title(doc, toc_outline)
    if toc_outline:  # Use TOC directly if available
        return {"title": title, "outline": toc_outline}

    # Fallback: regex heading detection
    all_headings = []
    seen_headings = set()
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        all_headings.extend(regex_heading_detection(text, page_num, seen_headings))

    return {"title": title, "outline": all_headings}

# --------------------------
# 5) Save JSON
# --------------------------
def save_json(result, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

# --------------------------
# 6) Compare JSONs (Diff Comparison)
# --------------------------
def compare_jsons(json1_path, json2_path):
    with open(json1_path, "r", encoding="utf-8") as f1, open(json2_path, "r", encoding="utf-8") as f2:
        j1, j2 = json.load(f1), json.load(f2)

    h1 = {(h["level"], h["text"].strip()) for h in j1["outline"]}
    h2 = {(h["level"], h["text"].strip()) for h in j2["outline"]}

    missing = h2 - h1
    extra = h1 - h2

    sm = SequenceMatcher(None, json.dumps(j1, sort_keys=True), json.dumps(j2, sort_keys=True))
    similarity = sm.ratio() * 100

    print(f"\n=== JSON Comparison Report ===")
    print(f"Similarity Score: {similarity:.2f}%")
    if missing:
        print(f"\n❌ Missing Headings ({len(missing)}):")
        for m in sorted(missing):
            print(f"  - {m}")
    if extra:
        print(f"\n⚠️ Extra (Wrongly Detected) Headings ({len(extra)}):")
        for e in sorted(extra):
            print(f"  - {e}")
    if not missing and not extra:
        print("\n✅ Perfect Match!")

# --------------------------
# 7) Batch Process PDFs
# --------------------------
def process_all_pdfs(input_dir="./input", output_dir="./output"):
    os.makedirs(output_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.json")
            result = process_pdf(pdf_path)
            save_json(result, output_path)
            print(f"Saved: {output_path}")

if __name__ == "__main__":
    process_all_pdfs(input_dir="./input", output_dir="./output")
    # Example: Compare your generated output vs. expected JSON
    # compare_jsons("output/file03.json", "sample_file03.json")
