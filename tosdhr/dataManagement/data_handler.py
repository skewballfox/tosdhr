import json
from pathlib import Path
from time import sleep
from requests import request
from tosdhr.dataManagement.services import get_reviewed_documents, BookShelf, Borks


class DataHandler(object):
    """class for handling input data for the model, pretty much the only part
    of the code which should be interacting the with ToS;Dr website, or the
    data directory
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.services_dir = data_dir / "services"
        self.cases_dir = data_dir / "cases"

        # does nothing if directory already exists
        self.services_dir.mkdir(parents=True, exist_ok=True)

    def get_or_scrape(self, data_dir, file_name: str, url: str):

        file_path = data_dir / file_name
        if file_path.exists():
            with open(file_path, "r") as f:

                return json.loads(f.read())
        else:
            content = request("get", url).json()
            # added to avoid spamming ToS;Dr's API
            sleep(0.5)
            with open(file_path, "w") as f:
                print(f"writing {file_path}")
                json.dump(content, f)
            return content

    def get_all_services(self):
        return self.get_or_scrape(
            self.data_dir, "all_services.json", "https://api.tosdr.org/all-services/v1/"
        )

    def get_service(self, service_name: str, id: int):
        """function to get the json data associated with the service.
        NOTE: may wind up modifying the returned json to be only content relevant to building the model
        """
        return self.get_or_scrape(
            self.services_dir,
            service_name + ".json",
            f"https://api.tosdr.org/service/v1/?service={id}",
        )

    def get_case(self, case_id: int | str):
        return self.get_or_scrape(
            self.case_data_dir,
            str(case_id) + ".json",
            f"https://api.tosdr.org/case/v1/?case={case_id}",
        )

    def get_list_reviewed_services(self) -> list[str]:
        reviewed_list = []

        for service in self.get_all_services()["parameters"]["services"]:
            if service["is_comprehensively_reviewed"] == True:
                name: str = service["name"]
                id: int = service["id"]
                reviewed_list.append((name, id))
        print(len(reviewed_list))
        return reviewed_list

    def get_all_reviewed_documents(self):
        documents = BookShelf()
        borks = Borks()
        for (service_name, id) in self.get_list_reviewed_services():

            docs, new_borks = get_reviewed_documents(self.get_service(service_name, id))
            # if docs in documents:
            #     print("yeet")
            documents.update(docs)
            borks.update(new_borks)

        return documents, borks
