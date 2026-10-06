# py -m pip install --user pipx
# py -m pipx ensurepath

Set-Location $PSScriptRoot
py -3.10 -m pip install --user --editable .

# py -3.10 -m pip uninstall homelab-dashboard