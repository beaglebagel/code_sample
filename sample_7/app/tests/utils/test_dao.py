
"""
Test module for Data Access Object module.
"""

import pytest

from app.core.exception import ItemNotFoundError
from app.core.schema import Student, Exam, Score, ScoreType
from app.utils.dao import Dao


def test_get_put_student():
    test_dao = Dao()

    # empty case
    assert 0 == len(test_dao.get_student())

    # non existent id
    with pytest.raises(ItemNotFoundError):
        test_dao.get_student(student_id='invalid_student_id')

    # put 1 student and check.
    test_student_id = 'test_student_id'
    test_dao.put_student(Student(id=test_student_id))
    test_student = test_dao.get_student(student_id=test_student_id)
    assert [Student(id=test_student_id)] == test_student

    # put 2 students and check.
    test_student_id2 = 'test_student_id2'
    test_dao.put_student(Student(id=test_student_id2))
    test_students = test_dao.get_student()
    assert 2 == len(test_students)
    assert [Student(id=test_student_id), Student(id=test_student_id2)] == test_students


def test_get_put_exam():
    test_dao = Dao()

    # empty case
    assert 0 == len(test_dao.get_exam())

    # non existent id
    with pytest.raises(ItemNotFoundError):
        test_dao.get_exam(exam_id='invalid_exam_id')

    # put 1 exam and check.
    test_exam_id = 'test_exam_id'
    test_dao.put_exam(Exam(id=test_exam_id))
    test_exam = test_dao.get_exam(exam_id=test_exam_id)
    assert [Exam(id=test_exam_id)] == test_exam

    # put 2 exams and check.
    test_exam_id2 = 'test_exam_id2'
    test_dao.put_exam(Exam(id=test_exam_id2))
    test_exams = test_dao.get_exam()
    assert 2 == len(test_exams)
    assert [Exam(id=test_exam_id), Exam(id=test_exam_id2)] == test_exams


def test_get_put_score():
    test_dao = Dao()

    # non existent student id
    with pytest.raises(ItemNotFoundError):
        test_dao.get_score_by_student_id(student_id='invalid_student_id')

    # non existent exam id
    with pytest.raises(ItemNotFoundError):
        test_dao.get_score_by_exam_id(exam_id='invalid_exam_id')

    test_student_id = 'test_student_id'
    test_exam_id = 'test_exam_id'
    test_score = 100.0
    test_dao.put_score(Score(student_id=test_student_id,
                             exam_id=test_exam_id,
                             score=test_score,
                             type=ScoreType.REGULAR))

    test_score = Score(student_id=test_student_id,
                       exam_id=test_exam_id,
                       score=test_score,
                       type=ScoreType.REGULAR)

    assert [test_score] == test_dao.get_score_by_student_id(student_id=test_student_id)
    assert [test_score] == test_dao.get_score_by_exam_id(exam_id=test_exam_id)


def test_get_score_summary():
    test_dao = Dao()

    test_student_id = 'test_student_id'
    test_student_id2 = 'test_student_id_2'
    test_exam_id = 'test_exam_id'
    test_exam_id2 = 'test_exam_id2'
    test_score = 0.0
    test_score2 = 100.0

    test_scores_by_student = [
        Score(student_id=test_student_id,
              exam_id=test_exam_id,
              score=test_score,
              type=ScoreType.REGULAR),
        Score(student_id=test_student_id,
              exam_id=test_exam_id2,
              score=test_score2,
              type=ScoreType.REGULAR)
    ]

    test_scores_by_exam = [
        Score(student_id=test_student_id,
              exam_id=test_exam_id,
              score=test_score,
              type=ScoreType.REGULAR),
        Score(student_id=test_student_id2,
              exam_id=test_exam_id,
              score=test_score2,
              type=ScoreType.REGULAR)
    ]

    # empty input score list.
    with pytest.raises(ValueError):
        test_dao.get_score_summary(scores=[], student_id=test_student_id, exam_id=test_exam_id)

    # guard against both ids provided.
    with pytest.raises(ValueError):
        test_dao.get_score_summary(scores=[], student_id=test_student_id, exam_id=test_exam_id)

    # guard neither ids provided.
    with pytest.raises(ValueError):
        test_dao.get_score_summary(scores=[])

    # check for valid average Score Summary by student id.
    assert Score(score=50.0,
                 type=ScoreType.AVERAGE,
                 student_id=test_student_id) == \
           test_dao.get_score_summary(scores=test_scores_by_student,
                                      student_id=test_student_id)

    # check for valid average Score Summary by exam id.
    assert Score(score=50.0,
                 type=ScoreType.AVERAGE,
                 exam_id=test_exam_id) == \
           test_dao.get_score_summary(scores=test_scores_by_exam,
                                      exam_id=test_exam_id)
