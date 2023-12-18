

class ItemNotFoundError(Exception):
    """
    Custom Error to indicate item not found case.
    """
    def __init__(self, item_id: str):
        """
        Parameters
        ----------
        item_id: id of involved instance (Student, Exam etc)
        """
        self.item_id = item_id