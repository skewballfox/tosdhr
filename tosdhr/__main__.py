from pathlib import Path

from tosdhr.dataManagement.data_handler import DataHandler
from tosdhr.dataManagement.services import language_filter


data_dir: Path = Path(__file__).parent.parent / "data"
output_dir: Path = Path(__file__).parent.parent / "outputs"

data: DataHandler = DataHandler(data_dir)

documents, borks = data.get_all_reviewed_documents()
documents.prune()
language_filter(documents)

print(
    f"number of annotated documents: {len(documents)-documents.get_empty_doc_count()}"
)

case_set = documents.get_annotation_cases()
print(
    f"average, max, and min number of annotations per document {documents.get_annotation_stats()}"
)
print(f"total number of borked documents: {borks.get_number_borked_documents()}")
print(f"total number of annotations: {documents.get_annotation_count()}")
print(f"total number of borked annotations: {len(borks)}")
print(f"total number of distinct cases: {len(case_set)}")
