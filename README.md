# FastAPI Book Text Extractor

## Overview

This FastAPI service extracts character mentions and generates a summary from a given book passage.

## Features

Identifies characters mentioned in the passage
Returns the character occurrences with their start and end token positions

## Installation & Setup

### Prerequisites

Python 3.9+
Docker (optional, for containerized deployment)

### Local Setup

Clone the repository:

```sh
git clone <repo-url>
cd <repo-folder>
```

## Docker Setup

Build the Docker image:

```sh
docker buildx build --platform linux/arm64 --no-cache -t fastapi-extract-info --load .

```

````

Run the container:

```sh
docker run -p 8000:8000 fastapi-extract-info
````

## API Usage

```bash
curl -X 'POST' \
  "http://localhost:8000/extract_information" \
  -H "Content-Type: application/json" \
  -d "{
    \"book_text\": \"Harry Potter and the Sorcerer's Stone follows the story of a young wizard, Harry, as he discovers his magical abilities and faces challenges.\"
  }"
```

```bash
curl -X 'POST' \
  "http://localhost:8000/extract_information" \
  -H "Content-Type: application/json" \
  --data-binary @book.json
```

Response:

```json
{
  "summary": "Generated summary of the book text.",
  "characters": [
    {
      "name": "Character Name",
      "occurrences": [
        {
          "token_id_start": 10,
          "token_id_end": 20
        }
      ]
    }
  ]
}
```

## Observations & Challenges

Character Identification: The model relies on spaCy's Named Entity Recognition (NER), which may miss some characters or misidentify them.
Summarization: The text summarization uses transformers from Hugging Face, which works well for short passages but may need adjustments for longer texts.
Scaling Considerations: Processing full books (e.g., 1,000+ chapters) would require a more efficient batch-processing approach, possibly using job queues like Celery or distributed processing frameworks.
Future Improvements
Improve character extraction accuracy with custom-trained models.
Implement caching for repeated requests.
Scale the service using Kubernetes or cloud functions for large datasets.

```

```

TODO:

Add docstrings
Check why length of summary is not the same as config
Remove comments
Answer questions
