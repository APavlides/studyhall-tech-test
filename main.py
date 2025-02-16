import re

import spacy
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Load NLP models
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization")


class BookTextRequest(BaseModel):
    book_text: str


def extract_characters(text: str):
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


def generate_summary(text: str):
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]["summary_text"]


@app.post("/extract_information")
async def extract_information(request: BookTextRequest):
    if not request.book_text:
        raise HTTPException(status_code=400, detail="Book text is required")

    summary = generate_summary(request.book_text)
    characters = extract_characters(request.book_text)

    return {"summary": summary, "characters": characters}


# Run using: uvicorn main:app --reload
