"""Split parsed documents into overlapping chunks."""

import re
from dataclasses import dataclass

from transformers import AutoTokenizer

from core.config import EMBEDDING_MODEL
from core.parser import ParsedDocument


@dataclass
class Chunk:
    """One piece of a document, with its source metadata."""

    text: str
    filename: str
    path: str
    chunk_index: int


class TextChunker:
    """Splits document text into overlapping chunks of roughly a target token size."""

    SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

    def __init__(self, chunk_size: int = 500, overlap: int = 60) -> None:
        self.chunk_size: int = chunk_size
        self.overlap: int = overlap
        self.tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)

    def count_tokens(self, text: str) -> int:
        """How many tokens this text becomes."""
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def chunk_document(self, document: ParsedDocument) -> list[Chunk]:
        """Split a document into overlapping chunks."""
        paragraphs = self._prepare_paragraphs(document.text)
        chunks: list[Chunk] = []
        current: list[str] = []

        for paragraph in paragraphs:
            candidate = "\n\n".join([*current, paragraph])

            if current and self.count_tokens(candidate) > self.chunk_size:
                chunks.append(self._make_chunk(current, document, len(chunks)))
                current = self._overlap_tail(current)

            current.append(paragraph)

        if current:
            chunks.append(self._make_chunk(current, document, len(chunks)))

        return chunks

    def _prepare_paragraphs(self, text: str) -> list[str]:
        """Split on blank lines, breaking up any paragraph larger than a chunk."""
        paragraphs: list[str] = []

        for paragraph in text.split("\n\n"):
            if self.count_tokens(paragraph) > self.chunk_size:
                paragraphs.extend(self._split_paragraph(paragraph))
            else:
                paragraphs.append(paragraph)

        return paragraphs

    def _split_paragraph(self, paragraph: str) -> list[str]:
        """Split an oversized paragraph into sentence-sized pieces that fit."""
        pieces: list[str] = []
        current: list[str] = []

        for sentence in self.SENTENCE_END.split(paragraph):
            candidate = " ".join([*current, sentence])

            if current and self.count_tokens(candidate) > self.chunk_size:
                pieces.append(" ".join(current))
                current = []

            current.append(sentence)

        if current:
            pieces.append(" ".join(current))

        return pieces

    def _overlap_tail(self, paragraphs: list[str]) -> list[str]:
        """Carry the end of a chunk into the next one.

        Prefers whole paragraphs. If the last paragraph alone is bigger than
        the overlap budget, falls back to whole sentences from it, so the
        overlap is never cut mid-sentence.
        """
        tail: list[str] = []

        for paragraph in reversed(paragraphs):
            if self.count_tokens("\n\n".join([paragraph, *tail])) > self.overlap:
                break
            tail.insert(0, paragraph)

        if tail:
            return tail

        return self._sentence_tail(paragraphs[-1])

    def _sentence_tail(self, paragraph: str) -> list[str]:
        """Take trailing whole sentences from a paragraph, up to the budget."""
        tail: list[str] = []

        for sentence in reversed(self.SENTENCE_END.split(paragraph)):
            if self.count_tokens(" ".join([sentence, *tail])) > self.overlap:
                break
            tail.insert(0, sentence)

        return [" ".join(tail)] if tail else []

    def _make_chunk(self, paragraphs: list[str], document: ParsedDocument, index: int) -> Chunk:
        """Build a Chunk from collected paragraphs, inheriting document metadata."""
        return Chunk(
            text="\n\n".join(paragraphs),
            filename=document.filename,
            path=document.path,
            chunk_index=index,
        )