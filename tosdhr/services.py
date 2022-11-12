"""classes for handling data objects used for training the model"""


import sys


class Case(object):
    def __init__(self, case_id: int, description: str):
        self.id: int = case_id
        self.description: str = description


# use slots to make these objects relatively tiny
# https://wiki.python.org/moin/UsingSlots
class Annotation(object):
    def __init__(self, id: int, case_id: int, quote_start: int, quote_end: int):
        self.id: int = id  # may wind up deleting this
        self.case_id: int = case_id
        self.quote_start: int = quote_start
        self.quote_end: int = quote_end


# TODO: implement get_item to return slice of text by index of underlying list
# https://docs.python.org/3/reference/datamodel.html#object.__getitem__
class Document(object):
    def __init__(self, id: int, name: str, text: str):
        self.id: int = id
        self.name: str = name
        self.text: str = text  # maybe byte array?
        self.annotations: list[Annotation] = []

    def add_annotation(self, point_id, case_id, quote_start, quote_stop):
        # todo, verify annotation isn't already in
        # the list of annotations
        self.annotations.append(Annotation(point_id, case_id, quote_start, quote_stop))

    # def __getitem__(self, item):
    #    return self.text[item]


def get_reviewed_documents(service_json: dict) -> dict:
    documents = {}
    documents
    for doc in service_json["parameters"]["documents"]:
        id: int = doc["id"]
        documents[id] = Document(id, doc["name"], doc["text"])
    for point in service_json["parameters"]["points"]:
        if point["status"] == "approved" and point["document_id"] is not None:
            # print(point)
            point_id: int = point["id"]
            doc_id: int = point["document_id"]
            case_id: int = point["case_id"]
            start: int = point["quoteStart"]
            stop: int = point["quoteEnd"]
            # print(documents[doc_id])
            if documents[doc_id].text[start:stop] != point["quoteText"]:
                print(service_json["parameters"]["name"])
                print(documents[doc_id].name)
                print(
                    f"slice text:\n{documents[doc_id].text[start:stop]}\nquote text\n",
                    point["quoteText"],
                )
                sys.exit()
            documents[doc_id].add_annotation(point_id, case_id, start, stop)
    return documents
