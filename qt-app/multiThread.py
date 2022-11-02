from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time


def longRunningFunction():
    for i in range(5):
            time.sleep(20)

def runInNewThread(self, taskFunction):
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(taskFunction)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # worker.progress.connect(reportProgress)
        # Step 6: Start the thread
        self.thread.start()


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, taskFunction):
        super(Worker, self).__init__()
        self.task = taskFunction

    def run(self):
        """Long-running task."""
        self.task()
        self.finished.emit()