"""Read markdown files from a directory and extract text with metadata."""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedDocument:
    """One markdown file: its text and where it came from."""

    text: str
    filename: str
    path: str


class DocumentParser:
    """Reads markdown files from a directory."""

    HTML_TAG = re.compile(
    r"</?(?:div|span|p|br|hr|a|img|table|tr|td|th|ul|ol|li|"
    r"h[1-6]|b|i|u|em|strong|code|pre|blockquote)\b[^>]*>",
    re.IGNORECASE,
   )

    def parse_directory(self, directory: str) -> list[ParsedDocument]:
        """Read every .md file in a directory. Skips files that can't be read."""
        documents: list[ParsedDocument] = []

        for file_path in sorted(Path(directory).glob("*.md")):
            document = self.parse_file(file_path)
            if document is not None:
                documents.append(document)

        return documents

    def parse_file(self, file_path: Path) -> ParsedDocument | None:
        """Read one markdown file. Returns None if it can't be read."""
        try:
            raw_text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            print(f"Skipping {file_path}: {error}")
            return None

        clean_text = self.HTML_TAG.sub("", raw_text).strip()

        if not clean_text:
            print(f"Skipping {file_path}: file is empty")
            return None

        return ParsedDocument(
            text=clean_text,
            filename=file_path.name,
            path=str(file_path),
        )