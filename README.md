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
must install package xxx first
```
textual run --dev <name-of-file>
```