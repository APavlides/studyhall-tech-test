import re

import spacy
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

SUMMARIZATION_MAX_LENGTH = config["summarization"]["max_length"]
SUMMARIZATION_MIN_LENGTH = config["summarization"]["min_length"]
CHUNK_SIZE = config["summarization"]["chunk_size"]

# Load NLP models (uses default models)
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization")


class BookTextRequest(BaseModel):
    book_text: str


def extract_characters(text: str):
    """
    Extracts character names from the given text using Named Entity Recognition (NER).

    :param text: The input text from which to extract character names.
    :type text: str
    :return: A list of dictionaries, each containing a character's name and their occurrences.
    :rtype: list[dict]

    Example output:
    .. code-block:: python

        [
            {"name": "John", "occurrences": [{"token_id_start": 15, "token_id_end": 19}]},
            {"name": "Alice", "occurrences": [{"token_id_start": 54, "token_id_end": 59}]}
        ]
    """
    doc = nlp(text)
    character_occurrences = {}

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if ent.text not in character_occurrences:
                character_occurrences[ent.text] = []

            start_idx = ent.start_char
            end_idx = ent.end_char
            character_occurrences[ent.text].append(
                {"token_id_start": start_idx, "token_id_end": end_idx}
            )

    return [
        {"name": name, "occurrences": occurrences}
        for name, occurrences in character_occurrences.items()
    ]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE):
    """
    Splits text into smaller chunks while maintaining sentence boundaries.

    This ensures that the summarization model does not exceed its token limit.

    :param text: The input text to be chunked.
    :type text: str
    :param chunk_size: The maximum number of characters per chunk (default is from config).
    :type chunk_size: int
    :return: A list of text chunks.
    :rtype: list[str]
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)  # Split on sentence endings
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def generate_summary(text: str):
    """
    Generates a summary for the given text, handling large inputs by chunking.

    :param text: The input text to be summarized.
    :type text: str
    :return: A summarized version of the input text.
    :rtype: str
    """
    print("text:", text)
    chunks = chunk_text(text)
    summaries = []

    print("chunks:", chunks)

    for chunk in chunks:
        try:
            summary = summarizer(
                chunk,
                max_length=SUMMARIZATION_MAX_LENGTH,
                min_length=SUMMARIZATION_MIN_LENGTH,
                do_sample=False,
            )[0]["summary_text"]
            summaries.append(summary)
            print("summaries:", summaries)
        except Exception as e:
            summaries.append("[Summary unavailable due to error]")  # Fallback text
            print(f"Summarization error: {e}")  # Debugging log

    return " ".join(summaries)  # Merge summaries


@app.post("/extract_information")
async def extract_information(request: BookTextRequest):
    if not request.book_text:
        raise HTTPException(status_code=400, detail="Book text is required")

    summary = generate_summary(request.book_text)
    characters = extract_characters(request.book_text)

    return {"summary": summary, "characters": characters}
