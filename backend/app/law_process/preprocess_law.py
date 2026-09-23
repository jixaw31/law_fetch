import re
from typing import Optional


# ---------------------------------------------------------
# Persian text normalization
# ---------------------------------------------------------

def normalize_text(text: str) -> str:
    replacements = {
        "\u064a": "ی",   # Arabic ي -> Persian ی
        "\u0649": "ی",
        "\u0643": "ک",   # Arabic ك -> Persian ک
        "\u200c": "‌",   # preserve ZWNJ
        "\u200f": "",
        "\u200e": "",
        "\r\n": "\n",
        "\r": "\n",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize multiple spaces, but preserve newlines
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive empty lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------
# Structural headings
# ---------------------------------------------------------

STRUCTURE_PATTERNS = {
    "volume": re.compile(
        r"^(جلد\s+[^\n]+)$"
    ),

    "book": re.compile(
        r"^(کتاب\s+[^\n]+)$"
    ),

    "chapter": re.compile(
        r"^(باب\s+[^\n]+)$"
    ),

    "section": re.compile(
        r"^(فصل\s+[^\n]+)$"
    ),

    "subsection": re.compile(
        r"^(مبحث\s+[^\n]+)$"
    ),

    "subsubsection": re.compile(
        r"^(گفتار\s+[^\n]+)$"
    ),
}


# ---------------------------------------------------------
# Article
# ---------------------------------------------------------

ARTICLE_RE = re.compile(
    r"""
    (?<!\S)
    ماده
    \s*
    (?P<number>\d+)
    (?P<status>
        \s*
        \(
        (?P<status_text>[^)]*)
        \)
    )?
    \s*
    (?P<content>.*?)
    (?=
        \n\s*ماده\s+\d+
        |
        \Z
    )
    """,
    re.VERBOSE | re.DOTALL,
)


# ---------------------------------------------------------
# Amendment information
#
# Examples:
# ماده 1 (اصلاحی 14ˏ08ˏ1370)
# ماده 2 (اصلاحی 29ˏ08ˏ1348)
# ---------------------------------------------------------

AMENDMENT_RE = re.compile(
    r"""
    اصلاحی
    \s*
    (?P<date>
        \d{1,4}
        [./ˏ،\-]
        \d{1,2}
        [./ˏ،\-]
        \d{1,4}
    )
    """,
    re.VERBOSE,
)


# ---------------------------------------------------------
# Other legal statuses
# ---------------------------------------------------------

STATUS_PATTERNS = {
    "اصلاحی": re.compile(r"\bاصلاحی\b"),
    "الحاقی": re.compile(r"\bالحاقی\b"),
    "منسوخه": re.compile(r"\bمنسوخه\b"),
    "موقوف الاجرا": re.compile(r"موقوف[\s‌]+الاجرا"),
    "احیاء": re.compile(r"\bاحیاء\b"),
    "تفسیر": re.compile(r"\bتفسیر\b"),
}

LAW_HEADER_RE = re.compile(
    r"""
    ^(?P<title>.*?)
    \s+
    مصوب
    \s+
    (?P<date>\d{4}[,./]\d{1,2}[,./]\d{1,2})
    (?P<rest>.*)$
    """,
    re.VERBOSE
)


def parse_law_header(text: str) -> dict:
    first_line = text.splitlines()[0].strip()

    match = LAW_HEADER_RE.match(first_line)

    if not match:
        return {
            "law_title": first_line,
            "law_date": None,
            "law_header": first_line,
        }

    return {
        "law_title": match.group("title").strip(),
        "law_date": normalize_date(match.group("date")),
        "law_header": first_line,
    }


def normalize_date(date: str) -> str:
    date = date.replace(",", "/")
    date = date.replace(".", "/")
    date = date.replace("ˏ", "/")
    date = date.replace("،", "/")
    date = date.replace("-", "/")

    parts = date.split("/")

    if len(parts) != 3:
        return date

    # Source occasionally uses day/month/year-like notation
    # depending on where the date occurs.
    return "/".join(parts)

def parse_article_status(status_text: Optional[str]):
    if not status_text:
        return {
            "article_status": "اصلی",
            "amendment_date": None,
        }

    status_text = status_text.strip()

    amendment_match = AMENDMENT_RE.search(status_text)

    if amendment_match:
        return {
            "article_status": "اصلاحی",
            "amendment_date": normalize_date(
                amendment_match.group("date")
            ),
        }

    for status, pattern in STATUS_PATTERNS.items():
        if pattern.search(status_text):
            return {
                "article_status": status,
                "amendment_date": None,
            }

    return {
        "article_status": status_text,
        "amendment_date": None,
    }

def detect_structure(line: str):
    line = line.strip()

    for level, pattern in STRUCTURE_PATTERNS.items():
        match = pattern.match(line)

        if match:
            return level, match.group(1).strip()

    return None, None

def finalize_article(
    article: dict,
    law_metadata: dict,
    articles: list[dict],
):

    content = " ".join(
        article.pop("content_parts")
    ).strip()

    hierarchy = article.pop("hierarchy")

    hierarchy_list = [
        law_metadata["law_title"]
    ]

    for level in hierarchy:
        if hierarchy[level]:
            hierarchy_list.append(
                hierarchy[level]
            )

    hierarchy_list.append(
        f"ماده {article['article_number']}"
    )

    embedding_text = (
        "\n".join(hierarchy_list)
        + "\n\n"
        + content
    )

    result = {
        "law_title": law_metadata["law_title"],
        "law_date": law_metadata["law_date"],

        **hierarchy,

        "article_number": article["article_number"],
        "article_status": article["article_status"],
        "amendment_date": article["amendment_date"],

        "content": content,

        "hierarchy": hierarchy_list,

        "embedding_text": embedding_text,
    }

    articles.append(result)

def parse_law(text: str) -> list[dict]:

    text = normalize_text(text)

    law_metadata = parse_law_header(text)

    hierarchy = {
        "volume": None,
        "book": None,
        "chapter": None,
        "section": None,
        "subsection": None,
        "subsubsection": None,
    }

    articles = []

    # -----------------------------------------------------
    # Split document into lines
    # -----------------------------------------------------

    lines = text.splitlines()

    current_article = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # -------------------------------------------------
        # Structural heading
        # -------------------------------------------------

        level, value = detect_structure(line)

        if level:

            hierarchy[level] = value

            # Clear deeper hierarchy
            levels = list(hierarchy.keys())
            index = levels.index(level)

            for deeper_level in levels[index + 1:]:
                hierarchy[deeper_level] = None

            continue

        # -------------------------------------------------
        # Article start
        # -------------------------------------------------

        article_match = re.match(
            r"^ماده\s+(\d+)"
            r"(?:\s*\(([^)]*)\))?"
            r"\s*(.*)$",
            line,
        )

        if article_match:

            # Save previous article
            if current_article:
                finalize_article(
                    current_article,
                    law_metadata,
                    articles,
                )

            number = int(article_match.group(1))
            status_text = article_match.group(2)
            content = article_match.group(3).strip()

            status = parse_article_status(status_text)

            current_article = {
                "article_number": number,
                "article_status": status["article_status"],
                "amendment_date": status["amendment_date"],
                "content_parts": [content] if content else [],
                "hierarchy": hierarchy.copy(),
            }

            continue

        # -------------------------------------------------
        # Article continuation
        # -------------------------------------------------

        if current_article:
            current_article["content_parts"].append(line)

    # -----------------------------------------------------
    # Final article
    # -----------------------------------------------------

    if current_article:
        finalize_article(
            current_article,
            law_metadata,
            articles,
        )

    return articles



import json

async def get_structured_law():
    with open("test_text.txt", "r", encoding="utf-8") as f:
        text = f.read()

    print("LEN TEXT:", len(text))

    articles = parse_law(text)

    # Save parsed articles
    with open(
        f"structured_laws/{articles[0]['law_title']}.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            articles,
            f,
            ensure_ascii=False,
            indent=2
        )
    
    print(f"Saved {len(articles)} articles to structured_laws/{articles[0]['law_title']}.json")

import asyncio
if __name__ == "__main__":
    asyncio.run(get_structured_law())