from __future__ import annotations
import re

SECTION_PATTERNS = {
    "title": r"TITLE:\s*(.+?)(?:\n[A-Z][A-Z_ ]+:|\Z)",
    "summary": r"SUMMARY:\s*(.+?)(?:\n[A-Z][A-Z_ ]+:|\Z)",
    "content": r"CONTENT:\s*(.+?)(?:\nHASHTAGS:|\n[A-Z][A-Z_ ]+:|\Z)",
    "hashtags": r"HASHTAGS:\s*(.+?)(?:\n[A-Z][A-Z_ ]+:|\Z)",
    "keywords": r"KEYWORDS:\s*(.+?)(?:\n[A-Z][A-Z_ ]+:|\Z)",
    "image_prompt": r"IMAGE_PROMPT:\s*(.+?)(?:\n[A-Z][A-Z_ ]+:|\Z)",
}

def _extract_section(label: str, text: str) -> str:
    pattern = SECTION_PATTERNS[label]
    match = re.search(pattern, text, flags=re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()

def parse_final_output(raw_text: str) -> dict[str, object]:
    title = _extract_section("title", raw_text)
    summary = _extract_section("summary", raw_text)
    content = _extract_section("content", raw_text)
    hashtags_text = _extract_section("hashtags", raw_text)
    keywords_text = _extract_section("keywords", raw_text)
    image_prompt = _extract_section("image_prompt", raw_text)

    hashtags = re.findall(r"#\w+", hashtags_text or raw_text)
    keywords = [
        keyword.strip()
        for keyword in keywords_text.split(",")
        if keyword.strip()
    ]

    if not content:
        content = raw_text.strip()
    if not title:
        first_line = content.splitlines()[0].strip() if content.splitlines() else "Generated Content"
        title = first_line[:120]
    if not summary:
        summary = "AI-generated content ready for downstream automation."

    return {
        "title": title,
        "summary": summary,
        "content": content.strip(),
        "hashtags": hashtags,
        "keywords": keywords,
        "image_prompt": image_prompt,
    }
