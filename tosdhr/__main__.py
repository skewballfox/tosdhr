from pathlib import Path

from tosdhr.data_handler import DataHandler


data_dir: Path = Path(__file__).parent.parent / "data"

data: DataHandler = DataHandler(data_dir)

output_dir: Path = Path(__file__).parent.parent
