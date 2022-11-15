# TODO: add code for pulling case data on all cases, but
# filter it down to the cases we have annotations for
class Case(object):
    def __init__(self, case_id: int, description: str):
        self.id: int = case_id
        self.description: str = description
