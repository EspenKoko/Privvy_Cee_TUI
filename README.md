Getting started

## Setting up poetry
[install pipx](https://pipx.pypa.io/stable/how-to/install-pipx/#on-windows) if not already installed
```cmd
py -m pip install --user pipx
```

## Install Poetry if not already installed
[Install poetry](https://python-poetry.org/docs/#installation)
```cmd
pipx install poetry
```

## Configure poetry
```cmd
poetry config virtualenvs.in-project true
poetry install
.venv\Scripts\Activate.ps1
poetry env info
```

## Install Textual
https://textual.textualize.io/getting_started/

```cmd
pip install textual textual-dev
```

To exit the tui 

```
ctrl+q
```

To live update during debug
run the app module or the package entrypoint with Textual's dev runner:
```
.venv\Scripts\textual.exe run --dev privvy_cee_ui.app
```

Or run the app normally:
```
python -m privvy_cee_ui
```