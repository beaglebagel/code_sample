
"""
Test module for app.utils.data_handler.
Checks basic functionality of event producer / consumer routine.
"""

import time
import threading

from queue import Queue
from app.utils.data_handler import DataHandler
from unittest.mock import patch, Mock


def test_receive_score():

    with patch('app.utils.data_handler.SSEClient') as MockSSEClient:

        class Event:
            def __init__(self, data: str):
                self.data = data

        test_events = []
        for data in ['{"exam": "e1", "studentId": "s1", "score": 100.0}',
                     '{"exam": "e2", "studentId": "s2", "score": 50.0}']:
            test_events.append(Event(data=data))

        mock_sseclient = MockSSEClient.return_value
        mock_sseclient._connect.return_value = Mock()

        # simulate incoming events in sseclient instance.
        mock_sseclient.__iter__.return_value = iter(test_events)

        test_url = 'https://test_url.com'
        test_queue = Queue()
        test_thread = threading.Thread(target=DataHandler.receive_data,
                                       args=(test_url, test_queue),
                                       daemon=True)
        test_thread.start()

        time.sleep(3)
        assert test_queue.qsize() == 2


def test_process_score():

    with patch('app.utils.dao.Dao') as MockDao:
        test_queue = Queue()
        test_dao = MockDao.return_value
        test_dao.put_student.return_value = None
        test_dao.put_exam.return_value = None
        test_dao.put_score.return_value = None

        # put two items.
        for data in ['{"exam": "e1", "studentId": "s1", "score": 100.0}',
                     '{"exam": "e2", "studentId": "s2", "score": 50.0}']:
            test_queue.put(data)

        test_thread = threading.Thread(target=DataHandler.process_data,
                                       args=(test_dao, test_queue),
                                       daemon=True)
        test_thread.start()
        # put arbitrary stop for test thread to process.
        time.sleep(3)
        assert test_queue.qsize() == 0
        assert test_dao.put_student.call_count == 2
        assert test_dao.put_exam.call_count == 2
        assert test_dao.put_score.call_count == 2
