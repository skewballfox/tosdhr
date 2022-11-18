# Terms of Service; Didn't Have to Read

a model for annotating terms of services and privacy policies, trained on data available from [ToS;Dr](https://tosdr.org/), which hopefully will eventually make the jobs of the volunteers easier

## Getting Started

### Installation

The quickest way to get started is to use [poetry](https://python-poetry.org/) to install the dependencies

```sh
git clone https://github.com/skewballfox/tosdhr
cd tosdhr
poetry install
```

p.s. if you want to keep the virtual environment in the project folder (so vscode automatically detects it) run this command before `poetry install` inside the project folder

```sh
poetry config virtualenvs.in-project true --local
```

the `--local` flag makes it so that this setting only applies to this project, rather than being the default for every project. Remove it only if you want this to be the default behavior for every poetry managed project.
