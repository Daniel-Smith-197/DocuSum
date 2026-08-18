from fastapi import FastAPI, UploadFile
from fastapi.exceptions import HTTPException
import pymupdf
import docx
import io
from database import engine, session, Base, Summary, getRec, getSum
from sqlalchemy.orm import defer
from tasks import celery_app, work
from celery.result import AsyncResult

app = FastAPI()
Base.metadata.create_all(engine)

@app.post("/summarize", status_code = 202)
async def upload_file(file : UploadFile, mode : str):
    if file.content_type not in {"text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}:
        raise HTTPException(400, detail = "Invalid file type - must be either .txt, .pdf, or .docx")
    if mode not in {"brief", "detailed", "bullet_points"}:
        raise HTTPException(400, detail = "Type of summary must be either brief, detailed, or bullet_points")
    if file.content_type == "text/plain":
        text = await file.read()
        text = text.decode("utf-8")
        job = work.delay(text, mode, file.filename)
        return {"job_id": job.id}
    if file.content_type == "application/pdf":
        doc_text = ""
        doc = await file.read()
        doc = pymupdf.open(stream = doc, filetype = "pdf")
        for page in doc:
            text = page.get_text()
            doc_text += f"{text} "
        job = work.delay(doc_text, mode, file.filename)
        return {"job_id": job.id}
    if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = await file.read()
        doc = docx.Document(io.BytesIO(doc))
        paragraphs = doc.paragraphs
        doc_text = ""
        for para in paragraphs:
            doc_text += f"{para.text} "
        job = work.delay(doc_text, mode, file.filename)
        return {"job_id": job.id}

@app.get("/summaries/status/{job_id}")
async def status(job_id : str):
    ar = AsyncResult(job_id, app = celery_app)
    state = ar.state
    if state == "PENDING" or state == "FAILURE":
        return {"state": state}
    if state == "SUCCESS":
        return {"state": state, "result": ar.result}

@app.get("/summaries")
async def retrieve(amtSums : int):
    if amtSums > 100:
        raise HTTPException(400, detail = "Cannot retrieve more than 100 summaries at a time")
    if amtSums < 1:
        raise HTTPException(400, detail = "Number of summaries cannot be less than 1")
    sums = session.query(Summary).options(defer(Summary.summary)).limit(amtSums).all()
    sumsList = [getRec.model_validate(sum) for sum in sums]
    return sumsList

@app.get("/summaries/{id}")
async def retrieve_one(id : int):
    summary = session.query(Summary).filter_by(id = id).first()
    if summary is None:
        raise HTTPException(404, detail = "Summary not found")
    retSum = getSum.model_validate(summary)
    return retSum.model_dump()