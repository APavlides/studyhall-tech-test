# FastAPI Book Text Extractor

## Overview

This FastAPI service extracts character mentions and generates a summary from a given book passage.

## Installation & Setup

### Prerequisites

Docker \
Docker Compose \
MacOS (ARM64) operating system

### Instructions for how to run the service

Build the Docker image:

```sh
docker buildx build --platform linux/arm64 --no-cache -t fastapi-extract-info --load .
```

Run the container:

```sh
docker run -p 8000:8000 fastapi-extract-info
```

### API Usage

To send a string:

```bash
curl -X 'POST' \
  "http://localhost:8000/extract_information" \
  -H "Content-Type: application/json" \
  -d "{
    \"book_text\": \"There was no possibility of taking a walk that day. We had been wandering, indeed, in the leafless shrubbery an hour in the morning; but since dinner..\"
  }"
```

To attach a document:

```bash
curl -X 'POST' \
  "http://localhost:8000/extract_information" \
  -H "Content-Type: application/json" \
  --data-binary @book.json
```

Sample response:

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

## Questions

### Any observations you had about the data

The text was initially processed by replacing newlines with spaces to ensure cleaner input for the NLP pipeline. I did not conduct extensive preprocessing beyond this.

Potential observations for real-world data include:

- Inconsistent formatting (e.g., varying line breaks, special characters, or non-standard spacing).
- Presence of non-text elements, such as images, tables, or mathematical formulas, which could impact summarization quality.
- Named entity ambiguity, where different characters might share similar names or be referenced in various forms (e.g., "Dr. Watson" vs. "Watson").

## Any data or infrastructure challenges that would need to be overcome if this was used in production to extract characters from real books.

It depends on exact requirements, but some key challenges in a production setting include:

#### Scalability & Performance:

- Processing entire books requires efficient batch processing (e.g., job queues with Pub/Sub, or Kafka).
- A distributed processing framework like Apache Spark could improve parallelism for large datasets.
- Running NLP models at scale might require GPU acceleration or optimised transformer models (e.g., distilBERT instead of BART).

#### Data Quality & Preprocessing:

- Named Entity Recognition (NER) Challenges: Character names may be ambiguous, and different spellings or references (e.g., "Elizabeth" vs. "Liz") need to be handled.

#### Infrastructure & Deployment Considerations:

- A microservices architecture with Kubernetes (K8s) could ensure scalability and fault tolerance.

### How you would expand the service to process all the chapters in each of 1,000 books.

#### Optimised Model Execution:

- Consider the correct size of NLP model for the job, if you can use a smaller model this would improve efficiency and cost.
- Utilize GPU-based inference (e.g., TensorRT (this is the tool I was trying to remember in our conversation), ONNX Runtime) for faster processing.

#### Infrastructure & Deployment:

- Deploy the service using Kubernetes (K8s) and autoscaling to manage varying loads.
- Use a message queue to distribute book processing tasks across worker nodes.

#### Data and preprocessing

- In terms of the algorithm, I have already including chunking but optimising this for larger texts is important.
- There are usually some data quality issues within this amount of data that will appear from time to time unless the data has been carefully curated. For example images/figures that are required to understand the meaning of the text, or mathematical equations. There would need to be a preprocessing module to handle these cases if they exist.
