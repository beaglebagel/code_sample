
from typing import Any
from fastapi import FastAPI, status, Query

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.exception import ItemNotFoundError
from app.core.schema import Student, Exam, Score

from app.utils.constants import logger
from app.utils.dao import Dao
from app.utils.data_handler import DataHandler

# create webapp, attach dao.
app = FastAPI()
app.dao = Dao()


# Handler for ValueError - to wrap as HTTPResponseError
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": f"ValueError: {exc}"})


# Handler for custom ItemNotFoundError - to wrap as HTTPResponseError
@app.exception_handler(ItemNotFoundError)
async def item_not_found_error_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(status_code=404, content={"detail": f"Item {exc.item_id} not found"})


@app.on_event('startup')
def startup():
    logger.info('[app] starting')
    # start background event processor.
    DataHandler.start()


@app.on_event('shutdown')
def shutdown():
    logger.info('[app] shutdown')


@app.get("/", status_code=status.HTTP_200_OK)
def ping() -> dict:
    return {"status": "pong"}


@app.get("/students", response_model=list[Student], status_code=status.HTTP_200_OK)
def get_students() -> Any:
    """
    Get list of students who received at least one exam score.
    """
    students = app.dao.get_student()
    logger.debug(f'total students: {len(students)}')
    return students


@app.get("/students/{student_id}", response_model=list[Score], status_code=status.HTTP_200_OK)
def get_students(student_id: str) -> Any:
    """
    Get a specific student's test results + average score across all exams.
    """
    scores = app.dao.get_score_by_student_id(student_id=student_id)
    logger.debug(f'total student scores: {len(scores)}')
    # append average score as the last record.
    return scores + [app.dao.get_score_summary(student_id=student_id, scores=scores)]


@app.get("/exams", response_model=list[Exam], status_code=status.HTTP_200_OK)
def get_exams() -> Any:
    """
    Get list of all recorded exams.
    """
    exams = app.dao.get_exam()
    logger.debug(f'total exams: {exams}')
    return exams


@app.get("/exams/{exam_id}", response_model=list[Score], status_code=status.HTTP_200_OK)
def get_exams(exam_id: str) -> Any:
    """
    Get a specific exam's test results + average score across all students.
    """
    scores = app.dao.get_score_by_exam_id(exam_id=exam_id)
    logger.debug(f'total exam scores: {len(scores)}')
    # append average score as the last record.
    return scores + [app.dao.get_score_summary(exam_id=exam_id, scores=scores)]

