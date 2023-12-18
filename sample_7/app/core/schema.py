
from enum import Enum
from pydantic import BaseModel


class ScoreType(str, Enum):
    """
    ScoreType conveys different types of Score info (extendable per needs).
    REGULAR indicates plain score info with student, exam info.
    AVERAGE & etc indicates summary type score info.
    """

    REGULAR = 'REGULAR'
    AVERAGE = 'AVERAGE'


class Student(BaseModel):
    """
    Student class for holding student info (e.g. id)
    """
    id: str


class Exam(BaseModel):
    """
    Exam class for holding exam info (e.g. id)
    """
    id: str


class Score(BaseModel):
    """
    Score class for holding score info.
    """
    score: float
    type: ScoreType = None
    exam_id: str | None = None
    student_id: str | None = None
