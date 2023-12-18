
"""
Test module for Main API-Layer to mainly checks on http status code in various scenarios.
"""

import json
import pytest

from app.main import app
from app.core.schema import Student, Exam, Score, ScoreType
from fastapi.testclient import TestClient

client = TestClient(app)

TEST_STUDENT_ID = 'test_student_id'
TEST_STUDENT_ID_WRONG = 'test_student_id_wrong'
TEST_EXAM_ID = 'test_exam_id'
TEST_EXAM_ID_WRONG = 'test_exam_id_wrong'


@pytest.fixture(autouse=True, scope='module')
def test_data():
    test_student = Student(id=TEST_STUDENT_ID)
    test_exam = Exam(id=TEST_EXAM_ID)
    test_score = Score(student_id=test_student.id,
                       exam_id=test_exam.id,
                       score=100.0,
                       type=ScoreType.REGULAR)
    test_score_by_student = Score(student_id=test_student.id,
                                      exam_id=None,
                                      score=100.0,
                                      type=ScoreType.AVERAGE)
    test_score_by_exam = Score(student_id=None,
                               exam_id=test_exam.id,
                               score=100.0,
                               type=ScoreType.AVERAGE)
    test_dict = {
        'test_student': test_student,
        'test_exam': test_exam,
        'test_score': test_score,
        'test_score_by_student': test_score_by_student,
        'test_score_by_exam': test_score_by_exam
    }

    # setup up initial dao data
    app.dao.put_student(test_dict['test_student'])
    app.dao.put_exam(exam=test_dict['test_exam'])
    app.dao.put_score(score=test_dict['test_score'])

    yield test_dict


def test_get_students(test_data):
    response = client.get('/students')
    assert response.status_code == 200
    assert response.json() == [json.loads(test_data['test_student'].model_dump_json())]


def test_get_student_scores_by_id(test_data):
    response = client.get(f'/students/{TEST_STUDENT_ID_WRONG}')
    assert response.status_code == 404

    response = client.get(f'/students/{TEST_STUDENT_ID}')
    assert response.status_code == 200
    assert response.json() == [
        json.loads(test_data['test_score'].model_dump_json()),
        json.loads(test_data['test_score_by_student'].model_dump_json())
    ]


def test_get_exams(test_data):
    response = client.get('/exams')
    assert response.status_code == 200
    assert response.json() == [json.loads(test_data['test_exam'].model_dump_json())]


def test_get_exam_scores_by_id(test_data):
    response = client.get(f'/exams/{TEST_EXAM_ID_WRONG}')
    assert response.status_code == 404

    response = client.get(f'/exams/{TEST_EXAM_ID}')
    assert response.status_code == 200
    assert response.json() == [
        json.loads(test_data['test_score'].model_dump_json()),
        json.loads(test_data['test_score_by_exam'].model_dump_json())
    ]