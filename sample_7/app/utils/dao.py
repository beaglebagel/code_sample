import statistics
from collections import defaultdict

from app.core.exception import ItemNotFoundError
from app.core.schema import Student, Exam, Score, ScoreType


class Dao:
    """
    Data Container + Access Objects for Student, Exam, Score data.
    This simulates data storage (in-memory) + data access layer.
    """

    # In-memory storage of Student, Exam, Score data.
    # student id -> list[student]
    STUDENT_MAP: dict[str, Student] = {}
    # student id -> list[score]
    STUDENT_SCORES: dict[str, list[Score]] = defaultdict(list)
    # exam id -> list[ (exam) ]
    EXAM_MAP: dict[str, Exam] = {}
    # exam id -> list[score]
    EXAM_SCORES: dict[str, list[Score]] = defaultdict(list)

    def get_student(self, student_id: str = None) -> list[Student]:
        """
        Get Student info from internal storage.

        Parameters
        ----------
        student_id : student id to search for. If not provided, returns all student info.

        Returns
        -------
        list of Student instances
        """
        if not student_id:
            return list(self.STUDENT_MAP.values())
        elif student_id not in self.STUDENT_MAP:
            raise ItemNotFoundError(item_id=student_id)
        return [self.STUDENT_MAP[student_id]]

    def put_student(self, student: Student) -> None:
        """
        Store Student Info into internal storage.

        Parameters
        ----------
        student : student instance to save.

        """
        self.STUDENT_MAP[student.id] = student

    def get_exam(self, exam_id: str = None) -> list[Exam]:
        """
        Get Exam info from internal storage.

        Parameters
        ----------
        exam_id : exam id to search for. If not provided, return all exam info.

        Returns
        -------
        list of Exam instances
        """
        if not exam_id:
            return list(self.EXAM_MAP.values())
        elif exam_id not in self.EXAM_MAP:
            raise ItemNotFoundError(item_id=exam_id)
        return [self.EXAM_MAP[exam_id]]

    def put_exam(self, exam: Exam) -> None:
        """
        Store Exam Info into internal storage.

        Parameters
        ----------
        exam : exam instance to save.

        """
        self.EXAM_MAP[exam.id] = exam

    def get_score_by_student_id(self, student_id: str) -> list[Score]:
        """
        Get Scores per student id from internal storage.

        Parameters
        ----------
        student_id : student id to get Scores for.

        Returns
        -------
        list of Score instances
        """
        if student_id not in self.STUDENT_SCORES:
            raise ItemNotFoundError(item_id=student_id)
        return self.STUDENT_SCORES[student_id]

    def get_score_by_exam_id(self, exam_id: str) -> list[Score]:
        """
        Get Scores per exam id from internal storage.

        Parameters
        ----------
        exam_id : exam id to get Scores for.

        Returns
        -------
        list of Exam instances
        """
        if exam_id not in self.EXAM_SCORES:
            raise ItemNotFoundError(item_id=exam_id)
        return self.EXAM_SCORES[exam_id]

    def put_score(self, score: Score) -> None:
        """
        Store Score Info into internal storage.
        Score is assorted in two different ways.
        - by student id
        - by exam id
        This allows simple lookup of scores based on either identifiers.

        Parameters
        ----------
        score : Score instance to save

        """
        self.STUDENT_SCORES[score.student_id].append(score)
        self.EXAM_SCORES[score.exam_id].append(score)

    @staticmethod
    def get_score_summary(scores: list[Score],
                          student_id: str = None,
                          exam_id: str = None) -> Score:
        """
        Helper method to prepare summary info from score, student, exam input.
        For the exercise, this prepares dedicated Score object of Average score info,
        and this can be extended further per need.

        **Note: the averages are calculated per either
            1. scores by one student
            2. scores by one exam
        Thus we expect only one of student_id or exam_id to be passed in.

        Parameters
        ----------
        scores : scores to calculate averages from.
        student_id : one student id of the score.
        exam_id : one exam id of the scores.
        ** only either onf of student_id or exam_id should be specified.

        Returns
        -------
        Score instance of Non-Regular type (Average as a start)
        that defines score summary.
        """
        if not scores:
            raise ValueError('empty scores not allowed.')
        elif not student_id and not exam_id:
            raise ValueError('neither student_id nor exam_id provided.')
        elif student_id and exam_id:
            raise ValueError('only one of student_id or exam_id should be provided.')

        avg_score = Score(student_id=student_id,
                          exam_id=exam_id,
                          type=ScoreType.AVERAGE,
                          score=statistics.mean([sc.score for sc in scores]))
        return avg_score
