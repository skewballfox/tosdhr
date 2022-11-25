"""classes for handling data objects used for training the model"""


import sys
from typing import Optional
from enum import Enum
from polyglot.detect import Detector
from collections import Counter

borked_annotations = 0
borked_docs = set()
borked_services = set()


class BorkType(Enum):
    MissingDocument = 1
    MissingQuote = 2
    NoQuote = 3


class BorkedAnnotations(object):
    __slots__ = ["id", "doc_id", "quote_text", "approved", "case_id", "title", "type"]

    def __init__(
        self, id, doc_id, case_id, quote_text, approved_flag, title, bork_type
    ):
        self.id: int = id
        self.doc_id = doc_id
        self.quote_text = quote_text
        self.approved = approved_flag
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
        approved_flag: bool,
        title: str,
        bork_type: BorkType,
    ):
        self.annotations.append(
            BorkedAnnotations(
                id, doc_id, case_id, quote_text, approved_flag, title, bork_type
            )
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
        approved_flag = point_json["status"]
        self.add_service(service_name)
        self.add_document(doc_id)
        self.add_annotation(
            point_id, doc_id, case_id, quote_text, approved_flag, title, bork_type
        )

    def update(self, more_borks: "Borks"):
        self.annotations.extend(more_borks.annotations)
        self.documents.update(more_borks.documents)
        self.services.update(more_borks.services)

    def __len__(self):
        return len(self.annotations)

    def get_number_borked_documents(self):
        return len(self.documents)


# use slots to make these objects relatively tiny
# https://wiki.python.org/moin/UsingSlots
class Annotation(object):
    __slots__ = ["id", "doc_id", "case_id", "approved", "quote_start", "quote_end"]

    def __init__(
        self,
        id: int,
        doc_id: int,
        case_id: int,
        approved_flag: bool,
        quote_start: int,
        quote_end: int,
    ):
        self.id: int = id  # may wind up deleting this
        self.doc_id = doc_id
        self.case_id: int = case_id
        self.approved = approved_flag
        self.quote_start: int = quote_start
        self.quote_end: int = quote_end

    @property
    def quote(self):
        return slice(self.quote_start, self.quote_end)


# TODO: implement get_item to return slice of text by index of underlying list
# https://docs.python.org/3/reference/datamodel.html#object.__getitem__
class Document(object):
    def __init__(self, id: int, name: str, text: str):
        self.id: int = id
        self.name: str = name
        self.text: str = text  # maybe byte array?
        self.annotations: list[Annotation] = []

    def add_annotation(self, point_id, case_id, approved_flag, quote_start, quote_stop):
        # todo, verify annotation isn't already in
        # the list of annotations
        self.annotations.append(
            Annotation(
                point_id,
                self.id,
                case_id,
                approved_flag,
                quote_start,
                quote_stop,
            )
        )

    def encode(self, encoding):
        self.text.encode(encoding)

    def get_annotation_case_counts(self):
        approved_cases = Counter()
        declined_cases = Counter()
        for annotation in self.annotations:
            if annotation.approved is True:
                approved_cases[annotation.case_id] += 1
            else:
                declined_cases[annotation.case_id] += 1
        return approved_cases, declined_cases

    def get_cases_dict(self):
        approved_cases = {}
        # TODO: add back later if good negative data can be found
        # declined_cases={}
        for annotation in self.annotations:
            if annotation.approved is True:
                approved_cases[annotation.case_id]

    def __getitem__(self, text_slice):
        return self.text[text_slice]

    def __iter__(self):
        return iter(self.annotations)

    def __len__(self):
        """returns the number of annotations of the document

        Returns:
            int: total number of valid annotations
        """
        return len(self.annotations)


class BookShelf(object):
    __slots__ = ["__documents"]

    def __init__(self):
        self.__documents: dict[int, Document] = {}

    def __getitem__(self, doc_id: int):
        return self.__documents[doc_id]

    def __setitem__(self, doc_id, doc):
        self.__documents[doc_id] = doc

    def __iter__(self):
        return iter(self.__documents)

    def __len__(self):
        return len(self.__documents)

    def update(self, other_bookshelf: "BookShelf"):
        self.__documents.update(other_bookshelf.__documents)

    def values(self):
        return self.__documents.values()

    def get_annotation_cases(self):
        approved_cases = Counter()
        declined_cases = Counter()
        for doc in self.__documents.values():
            approved, declined = doc.get_annotation_case_counts()
            approved_cases.update(approved)
        return approved_cases, declined_cases

    def get_annotation_count(self):
        count = 0
        for doc in self.__documents.values():
            count += len(doc)
        return count

    def get_empty_doc_count(self):
        count = 0
        for doc in self.__documents.values():
            if len(doc) == 0:
                count += 1
        return count

    def clean(self, language="English"):
        approved, declined = self.get_annotation_cases()
        approved_set = set(approved)
        declined_set = set(declined)

        # print(f"no positive data: {declined_set-approved_set}")
        self.prune()
        language_filter(self, language=language)

    def prune(self):
        """remove empty documents from the list of documents"""
        to_remove = []
        for k in self.__documents:
            if len(self.__documents[k]) == 0:
                to_remove.append(k)
        for doc_id in to_remove:
            self.__documents.pop(doc_id)

    def pop(self, doc_id):
        self.__documents.pop(doc_id)

    def get_average_annotation_count(self):
        number_of_docs = len(self)
        number_of_annotations = self.get_annotation_count()
        return number_of_annotations / number_of_docs

    def get_annotation_stats(self):
        """Returns information useful for understanding the quality of the data
        note you should call prune before this function, otherwise documents with no
        annotations will throw off the results

        Returns:
            float: average number of annotations per document
            int: max number of annotations in a document
            int: min number of annotations in a document
        """
        number_of_docs = len(self)
        annotation_count = 0
        max_count = -1
        min_count = 999999
        for doc in self.__documents.values():
            current_count = len(doc)
            annotation_count += current_count
            max_count = max(max_count, current_count)
            min_count = min(min_count, current_count)
        return annotation_count / number_of_docs, max_count, min_count

    def get_case_dict(self):
        cases = {}
        # declined_cases={}
        for doc in self.__documents.values():
            for annotation in doc:
                if annotation.approved:
                    if annotation.case_id in cases:
                        cases[annotation.case_id].append(doc[annotation.quote])
                    else:
                        cases[annotation.case_id] = [doc[annotation.quote]]
        return cases

    # TODO: add methods for getting stats such as average number of annotations per document,
    # total number of annotations, and total number of distinct cases


def language_filter(docs: BookShelf, language="English"):
    drop_list = []
    count = 0
    for document in docs.values():

        try:
            quote_language = Detector(document.text).language.name
            if quote_language != language:
                # print(f"quote lang: {quote_language}")
                drop_list.append(document.id)
        except Exception as e:
            # print(e)
            drop_list.append(document.id)
    print(f"dropping {len(drop_list)} documents due to language filter")
    for doc_id in drop_list:
        docs.pop(doc_id)


def get_reviewed_documents(service_json: dict) -> tuple[BookShelf, Borks]:
    documents = BookShelf()
    borks = Borks()
    for doc in service_json["parameters"]["documents"]:
        id: int = doc["id"]
        documents[id] = Document(id, doc["name"], doc["text"])
    for point in service_json["parameters"]["points"]:
        if point["document_id"] is not None:
            point_status = point["status"]
            if point_status == "approved" or point_status == "declined":
                approved_flag = True if point_status == "approved" else False
                # if approved_flag is False:
                #    print(point)
                point_id: int = point["id"]
                doc_id: int = point["document_id"]
                case_id: int = point["case_id"]
                start: int = point["quoteStart"]
                stop: int = point["quoteEnd"]
                if point["quoteText"] is None:
                    # if approved_flag is False:
                    #     print("declined and borked due to no quote text")

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
                    # if approved_flag is False:
                    #    print("declined and borked due to missing document")

                    continue
                if documents[doc_id].text[start:stop] != point["quoteText"]:

                    stop -= start
                    start = documents[doc_id].text.find(point["quoteText"])
                    stop += start
                    # print(f"new slice text:\n{documents[doc_id].text[start:stop]}")

                    if documents[doc_id].text[start:stop] != point["quoteText"]:
                        borks.add(
                            service_json["parameters"]["name"],
                            point,
                            BorkType.MissingQuote,
                        )
                        # if approved_flag is False:
                        #    print("declined and borked due to missing quote")
                        continue

                documents[doc_id].add_annotation(
                    point_id, case_id, approved_flag, start, stop
                )
            # the document being referenced doesn't exists

    return documents, borks
