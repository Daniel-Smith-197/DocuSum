# DocuSum

A REST API that summarizes uploaded documents. Upload a `.txt`, `.pdf`, or `.docx` file and get back a summary in one of three styles. Summarization runs as a background job, so uploads return immediately regardless of document length.

**Live:** [docusum-production.up.railway.app/docs](https://docusum-production.up.railway.app/docs)

## Stack

FastAPI · Celery · Redis · PostgreSQL · SQLAlchemy · Docker · OpenAI API

## Architecture

Summarizing a long document takes 30+ seconds, which is well past the point where HTTP clients and proxies drop a connection. Rather than hold the request open, the API hands the work to a background queue:

1. `POST /summarize` validates the upload, extracts text, and pushes a task to Redis
2. It returns a `job_id` immediately with a `202 Accepted`
3. A separate Celery worker process pulls the task, calls the OpenAI API, and writes the result to PostgreSQL
4. The client polls `GET /summaries/status/{job_id}` until the job reports `SUCCESS`

The API and the worker run as separate containers built from the same image, communicating only through Redis. Redis serves as both the task broker and the result backend; PostgreSQL holds the permanent record of every summary.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/summarize?mode=` | Upload a document. Returns a `job_id`. Modes: `brief`, `detailed`, `bullet_points` |
| `GET` | `/summaries/status/{job_id}` | Poll job state — `PENDING`, `SUCCESS`, or `FAILURE` |
| `GET` | `/summaries?amtSums=` | List past summaries with metadata (max 100) |
| `GET` | `/summaries/{id}` | Retrieve a single summary in full |

Supported uploads: `.txt`, `.pdf`, `.docx`. Text extraction uses PyMuPDF for PDFs and python-docx for Word files.

## Running locally

Requires Docker.

```bash
git clone https://github.com/Daniel-Smith-197/DocuSum.git
cd DocuSum
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY = sk-your-key-here
db_pass = your_postgres_password
db_url = postgresql://postgres:your_postgres_password@db:5432/document_summarizer
broker_url = redis://redis:6379/0
backend_url = redis://redis:6379/1
```

Then:

```bash
docker compose up --build
```

This starts four containers — the API, the Celery worker, PostgreSQL, and Redis. Interactive docs are at `http://localhost:8000/docs`.