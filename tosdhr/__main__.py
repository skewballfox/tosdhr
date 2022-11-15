from pathlib import Path

from tosdhr.dataManagement.data_handler import DataHandler


data_dir: Path = Path(__file__).parent.parent / "data"
output_dir: Path = Path(__file__).parent.parent / "outputs"

data: DataHandler = DataHandler(data_dir)

documents, borks = data.get_all_reviewed_documents()
print(len(documents))
print(len(borks))
