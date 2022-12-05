from pathlib import Path

from tosdhr.dataManagement.data_handler import DataHandler
from tosdhr.dataManagement.services import language_filter
import argparse


data_dir: Path = Path(__file__).parent.parent / "data"
output_dir: Path = Path(__file__).parent.parent / "outputs"

data: DataHandler = DataHandler(data_dir)


# print(f"total number of borked documents: {borks.get_number_borked_documents()}")
# print(f"total number of annotations: {documents.get_annotation_count()}")
# print(f"total number of borked annotations: {len(borks)}")
# print(f"total number of distinct cases: {len(approved_case_counter)}")
# print(f"approved case counter: {approved_case_counter}")
# print(f" case dict {case_dict}")
parser = argparse.ArgumentParser(description="So we can each use main")
parser.add_argument(
    "-s",
    "--topics",
    dest="topics_flag",
    action="store_true",
    help="run the topics scraper",
    default=False,
)
parser.add_argument(
    "-t",
    "--tokenize",
    dest="tokenize",
    help="test the tokenizer",
    action="store_true",
    # type=bool,
    default=False,
)
parser.add_argument(
    "-b",
    "--bert",
    dest="bert_flag",
    action="store_true",
    help="test the bert model",
    # type=bool,
    default=False,
)
parser.add_argument(
    "-c",
    "--cpu",
    dest="cpu_flag",
    action="store_true",
    help="test the bert model with cpu",
    # type=bool,
    default=False,
)
# might wanna add a parser argument for cpu or gpu enabling rather than just checking for cuda and using it either way
args = parser.parse_args()

if args.topics_flag:
    from tosdhr.dataManagement.data_handler import get_topics

    get_topics()
if args.t:

    documents, borks = data.get_all_reviewed_documents()
    documents.clean()
    documents.tokenize()
if args.bert_flag:
    from tosdhr.modelManager.bert import model

    pass
if args.cpu_flag:
    from tosdhr.modelManager.bert import model

    pass
# if no arguments have been passed
# https://stackoverflow.com/questions/10698468/argparse-check-if-any-arguments-have-been-passed
if not any(vars(args).values()):
    documents, borks = data.get_all_reviewed_documents()
    documents.clean()
    print(
        f"number of annotated documents: {len(documents)-documents.get_empty_doc_count()}"
    )

    approved_case_counter, decline_case_counter = documents.get_annotation_cases()
    case_set = set(approved_case_counter.keys())
    print(
        f"average, max, and min number of annotations per document {documents.get_annotation_stats()}"
    )
    case_dict = documents.get_case_dict()
