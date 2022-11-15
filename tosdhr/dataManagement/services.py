"""classes for handling data objects used for training the model"""


import sys
from typing import Optional
from enum import Enum

borked_annotations = 0
borked_docs = set()
borked_services = set()


class BorkType(Enum):
    MissingDocument = 1
    MissingQuote = 2
    NoQuote = 3


class BorkedAnnotations(object):
    __slots__ = ["id", "doc_id", "quote_text", "case_id", "title", "type"]

    def __init__(self, id, doc_id, case_id, quote_text, title, bork_type):
        self.id: int = id
        self.doc_id = doc_id
        self.quote_text = quote_text
        self.case_id = case_id
        self.title = title
        self.type: BorkType = bork_type


class Borks(object):
    def __init__(self):
        self.annotations = []
        self.documents = set()
        self.services = set()

    def add_annotation(
        self,
        id: int,
        doc_id: int,
        case_id: int,
        quote_text: Optional[str],
        title: str,
        bork_type: BorkType,
    ):
        self.annotations.append(
            BorkedAnnotations(id, doc_id, case_id, quote_text, title, bork_type)
        )

    def add_document(self, document):
        self.documents.add(document)

    def add_service(self, service_name):
        self.services.add(service_name)

    def add(self, service_name, point_json, bork_type):
        point_id: int = point_json["id"]
        doc_id: int = point_json["document_id"]
        case_id: int = point_json["case_id"]
        quote_text = point_json["quoteText"]
        title = point_json["title"]
        self.add_service(service_name)
        self.add_document(doc_id)
        self.add_annotation(point_id, doc_id, case_id, quote_text, title, bork_type)

    def update(self, more_borks: "Borks"):
        self.annotations.extend(more_borks.annotations)
        self.documents.update(more_borks.documents)
        self.services.update(more_borks.services)


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
        self.annotations.append(
            Annotation(
                point_id,
                case_id,
                quote_start,
                quote_stop,
            )
        )

    def __getitem__(self, text_slice):
        return self.text[text_slice]

    def __iter__(self):
        return iter(self.annotations)


class BookShelf(object):
    def __init__(self):
        self.__documents: dict[int, Document] = {}

    def __getitem__(self, doc_id: int):
        return self.__documents[doc_id]

    def __setitem__(self, doc_id, doc):
        self.__documents[doc_id] = doc

    def __iter__(self):
        return iter(self.__documents)

    def update(self, other_bookshelf: "BookShelf"):
        self.__documents.update(other_bookshelf.__documents)

    # TODO: add methods for getting stats such as average number of annotations per document,
    # total number of annotations, and total number of distinct cases


def get_reviewed_documents(service_json: dict) -> dict:
    documents = {}
    borks = Borks()
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
            print(point["source"])
            print(service_json["parameters"]["name"])
            print(start)
            if point["quoteText"] is None:
                borks.add(
                    service_json["parameters"]["name"],
                    point,
                    BorkType.NoQuote,
                )
                continue
            if doc_id not in documents:
                borks.add(
                    service_json["parameters"]["name"],
                    point,
                    BorkType.MissingDocument,
                )
                continue
            if documents[doc_id].text[start:stop] != point["quoteText"]:
                print(service_json["parameters"]["name"])
                print(documents[doc_id].name)
                print(
                    f"slice text:\n{documents[doc_id].text[start:stop]}\nquote text\n",
                    point["quoteText"],
                )

                stop -= start
                start = documents[doc_id].text.find(point["quoteText"])
                stop += start
                print(f"new slice text:\n{documents[doc_id].text[start:stop]}")

                if documents[doc_id].text[start:stop] != point["quoteText"]:
                    borks.add(
                        service_json["parameters"]["name"],
                        point,
                        BorkType.MissingQuote,
                    )
                    continue

            documents[doc_id].add_annotation(point_id, case_id, start, stop)
            # the document being referenced doesn't exists

    return documents, borks
