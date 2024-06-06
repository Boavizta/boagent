class InvalidPIDException(Exception):
    def __init__(self, pid):
        self.pid = pid
        self.message = f"Process_id {self.pid} has not been found in metrics data. Check the queried PID"
        super().__init__(self.message)
