"""Keep visible analysis headings sequential without altering translation keys."""
import re


def numbered_section(number: int, localized_heading: str) -> str:
    """Replace the historic section number while preserving translated heading text."""
    title = re.sub(r"^\s*[0-9０-９]+\s*[.．、)]\s*", "", localized_heading, count=1)
    return f"{number}. {title}"
