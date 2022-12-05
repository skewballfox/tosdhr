# TODO: add code for pulling case data on all cases, but
# filter it down to the cases we have annotations for
class Case(object):
    def __init__(self, case_id: int, description: str):
        self.id: int = case_id
        self.description: str = description
        self.approved_annotations = []
        self.declined_annotations = []


def get_topics(project_dir):
    # print(project_dir)
    s = Session()
    config = dotenv_values()
    print(config)
    response = s.get(
        "https://edit.tosdr.org/topics",
        auth=(config["USER"], config["PASSWORD"]),
    )
    soup = BeautifulSoup(response.content)
    soup.footer.decompose()
    # soup.body
    # partial url
    soup.select("a[href*=topics]")[0]
    for topic in soup.select("a[href*=topics]"):
        url = f"https://edit.tosdr.org/{topic.get('href')}"
        # title for topic
        topic_name = topic.next_element
        print(BeautifulSoup(s.get(url).content).body.prettify())
        break
        # contents also prints title

    print(s.get(url).content)


get_topics(None)
