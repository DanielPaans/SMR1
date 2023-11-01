import queue

class Queues():
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Queues.__instance == None:
            Queues()
        return Queues.__instance

    def __init__(self) -> None:
        if Queues.__instance is not None:
            raise Exception("An instance of Queues already exists. Use get_instance() to access it.")

        self.robot_data_queue = queue.Queue()
        self.robot_request_queue = queue.Queue()
        self.video_feed_queue = queue.Queue()
        self.logging_queue = queue.Queue()

        Queues.__instance = self