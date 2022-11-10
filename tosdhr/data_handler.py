import json
from pathlib import Path
from time import sleep
from requests import request


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

        file_path = self.data_dir / file_name
        if file_path.exists():
            with open(file_path, "r") as f:
                return json.loads(f.read())
        else:
            content = request("get", url).json()
            # added to avoid spamming ToS;Dr's API
            sleep(0.5)
            with open(file_path, "w") as f:
                json.dump(content, f)
            return content

    def get_all_services(self):
        return self.get_or_scrape(
            self.data_dir, "all_services.json", "https://api.tosdr.org/all-services/v1/"
        )

    def get_service(self, service_name: str):
        """function to get the json data associated with the service.
        NOTE: may wind up modifying the returned json to be only content relevant to building the model
        """
        return self.get_or_scrape(
            self.services_dir,
            service_name + ".json",
            f"https://api.tosdr.org/service/v1/?service={service_name}",
        )

    def get_case(self, case_id: int | str):
        return self.get_or_scrape(
            self.case_data_dir,
            str(case_id) + ".json",
            f"https://api.tosdr.org/case/v1/?case={case_id}",
        )

    def get_list_reviewed_services(self) -> list[str]:
        reviewed_list: list[str] = []
        for service in self.get_all_services()["parameters"]["services"]:
            if service["is_comprehensively_reviewed"] == True:
                reviewed_list.append(service["name"])
        return reviewed_list

    def get_reviewed_services(self):
        services = []
        for service_name in self.get_list_reviewed_services():
            services.append(self.get_service(service_name))
        return services
