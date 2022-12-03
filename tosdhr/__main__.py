from pathlib import Path

from tosdhr.dataManagement.data_handler import DataHandler
from tosdhr.dataManagement.services import language_filter

from tosdhr.modelManager.bert import model

data_dir: Path = Path(__file__).parent.parent / "data"
output_dir: Path = Path(__file__).parent.parent / "outputs"

data: DataHandler = DataHandler(data_dir)

documents, borks = data.get_all_reviewed_documents()
documents.clean()

case_dict = documents.get_case_dict()
print(
    f"number of annotated documents: {len(documents)-documents.get_empty_doc_count()}"
)

approved_case_counter, decline_case_counter = documents.get_annotation_cases()
case_set = set(approved_case_counter.keys())
print(
    f"average, max, and min number of annotations per document {documents.get_annotation_stats()}"
)
# print(f"total number of borked documents: {borks.get_number_borked_documents()}")
# print(f"total number of annotations: {documents.get_annotation_count()}")
# print(f"total number of borked annotations: {len(borks)}")
# print(f"total number of distinct cases: {len(approved_case_counter)}")
# print(f"approved case counter: {approved_case_counter}")
# print(f" case dict {case_dict}")
