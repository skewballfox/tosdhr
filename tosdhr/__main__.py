from pathlib import Path

from tosdhr.dataManagement.data_handler import DataHandler
from tosdhr.dataManagement.services import language_filter
import argparse
from pandas import DataFrame
from tosdhr.dataManagement.topics import get_topics
from tosdhr.modelManager.bert import Annotator, train, evaluate
from tosdhr.modelManager.torch_data import Dataset, train_val_test_split

data_dir: Path = Path(__file__).parent.parent / "data"
output_dir: Path = Path(__file__).parent.parent / "outputs"

data: DataHandler = DataHandler(data_dir)


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
    default=False,
)
parser.add_argument(
    "-c",
    "--cpu",
    dest="cpu_flag",
    action="store_true",
    help="test the bert model with cpu",
    default=False,
)
parser.add_argument(
    "-z",
    "--Zack",
    # dest="For Zack to test function calls",
    action="store_true",
    help="Zack Test code",
    default=False,
)
# might wanna add a parser argument for cpu or gpu enabling rather than just checking for cuda and using it either way
args = parser.parse_args()

if args.topics_flag:

    # use data
    documents, borks = data.get_all_reviewed_documents()
    documents.clean()
    df: DataFrame = documents.to_dataframe()
    # from toshdr.dataManagement.services import Bookshelf

    # TODO: Check if cases matches of get_topics and get_annotation_cases have any matching cases if so print them out

    get_topics()
if args.tokenize:

    documents, borks = data.get_all_reviewed_documents()
    documents.clean()

    approved_case_counter, decline_case_counter = documents.get_annotation_cases()
    # print(approved_case_counter)
    # print(decline_case_counter)
    case_set = set(approved_case_counter.keys())
    df = documents.to_dataframe()

    # print(f"raw text: {raw_text}")
    from tosdhr.modelManager.torch_data import Dataset, train_val_test_split


# think you can add a column to the dataframe for topics?
# What cha mean...? Isl it a Panda's dataframe?,sort of Polars I don't know Polars I can do some googling though if you need me to
# the syntax should be a drop in replacement for pandas, it's basically the same thing, but slightly faster
# Can you point me to where the dataframe you want me to modify is at?
if args.bert_flag:
    from tosdhr.modelManager.bert import Annotator, train, evaluate

    train(Annotator, train_data, val_data)
    evaluate(Annotator, test_data)

if args.cpu_flag:
    from tosdhr.modelManager.bert import Annotator, train, evaluate

    train(Annotator, train_data, val_data, use_cpu=True)
    evaluate(Annotator, test_data, use_cpu=True)


if args.Zack:
    # from tosdhr.dataManagement.services import

    documents, borks = data.get_all_reviewed_documents()
    documents.clean()

    # approved_case_counter, decline_case_counter = documents.get_annotation_cases()
    # # print(approved_case_counter)
    # # print(decline_case_counter)
    # case_set = set(approved_case_counter.keys())
    df = documents.to_dataframe()
    print(df)
    test_data, validation_data, train_data = train_val_test_split(df)
    from transformers import AutoModelForPreTraining

    legal_bert = AutoModelForPreTraining.from_pretrained(
        "nlpaueb/legal-bert-base-uncased"
    )

    train(legal_bert, train_data, validation_data)
    evaluate(Annotator, test_data)

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
    print(f"total number of borked documents: {borks.get_number_borked_documents()}")
    print(f"total number of annotations: {documents.get_annotation_count()}")
    print(f"total number of borked annotations: {len(borks)}")
    print(f"total number of distinct cases: {len(approved_case_counter)}")
    print(f"approved case counter: {approved_case_counter}")
    print(f" case dict {case_dict}")
