class InvalidPIDException(Exception):
    def __init__(self, pid):
        self.pid = pid
        self.message = f"Process_id {self.pid} has not been found in metrics data. Check the queried PID."
        super().__init__(self.message)


invalid_criteria_choice_error_msg = "Invalid criteria choice! You can query 'main' (Global Warming Potential (GWP), Abiotic Depletion Potential (ADP) and Primary Energy (PE)) or 'all' impact criteria."
