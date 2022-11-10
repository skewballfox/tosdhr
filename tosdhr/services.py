"""classes for handling data objects used for training the model"""
# use slots to make these objects relatively tiny
# https://wiki.python.org/moin/UsingSlots
class annotations(object):
    def __init__(self, case_id, quote_start: int, quote_end: int):
        self.case_id: int = case_id
        self.quote_start: int = quote_start
        self.quote_end: quote_end


# TODO: implement get_item to return slice of text by index of underlying list
# https://docs.python.org/3/reference/datamodel.html#object.__getitem__
class document(object):
    def __init__(self, document_json):
        self.id: int
        self.name: str
        self.text: str  # maybe byte array?
        self.annotations: list[annotations] = []


# NOTE: may wind up either removing this or storing separately
# from rest of data, only necessary for people or clustering
# documents, but *probably* useless for the model
class service(object):
    def __init__(self, service_json):
        self.id: int
        self.name: str
        self.documents = []
        self.cases = []
