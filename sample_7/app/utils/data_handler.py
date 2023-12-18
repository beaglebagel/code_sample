
import json
import threading

from queue import Queue
from app.core.schema import Student, Exam, Score, ScoreType
from app.utils.dao import Dao
from app.utils.constants import logger
from sseclient import SSEClient


URL = 'https://live-test-scores.herokuapp.com/scores'


class DataHandler:
    """
    DataHandler is a utlity class for handling score data through producer / consumer routine in asynchronous fashion.
    Receiver thread continuously ingests score events from api and drops onto shared queue.
    Processor thread continuously picks up the scores from shared queue and stores into internal storage.
    """

    @staticmethod
    def receive_data(url: str, queue: Queue) -> None:
        """
        Connects to live test score site and continuously ingests the data onto sharable queue.
        The data format in str '{"exam": 3, "studentId": "foo", score: .991}'

        Parameters
        ----------
        url : source site of SSE Event Data.
        queue : consumable queue to store event data onto.

        Returns
        -------

        """
        logger.info('receiver started')
        ssec = SSEClient(url=url)
        next(ssec)

        # blocks until further events.
        for msg in ssec:
            logger.info(f'[receive] {msg.data}')
            # data format: {"exam": 3, "studentId": "foo", score: .991}
            queue.put(msg.data)

    @staticmethod
    def process_data(dao: Dao, queue: Queue) -> None:
        """
        Continuously consumes score data from shared queue and stores in internal storage.

        Parameters
        ----------
        dao : interface to internal data storage.
        queue : consumable event data queue.

        Returns
        -------

        """
        logger.info('processor started')
        # blocks until queue gets populated.
        while queue:
            # data_str in {"exam": 3, "studentId": "foo", score: .991}
            data = json.loads(queue.get())
            logger.info(f'[process] {data}')
            student = Student(id=data['studentId'])
            exam = Exam(id=str(data['exam']))
            score = Score(exam_id=exam.id,
                          student_id=student.id,
                          score=data['score'],
                          type=ScoreType.REGULAR)
            dao.put_student(student=student)
            dao.put_exam(exam=exam)
            dao.put_score(score=score)

    @staticmethod
    def start() -> None:
        """
        Main entry point of DataHandler utility.
        Prepares data access object & sharable queue & spawns off producer / consumer threads to run on background.
        """
        dao = Dao()
        queue = Queue()
        receiver = threading.Thread(target=DataHandler.receive_data,
                                    args=(URL, queue),
                                    daemon=True)
        processor = threading.Thread(target=DataHandler.process_data,
                                     args=(dao, queue),
                                     daemon=True)
        receiver.start()
        processor.start()
