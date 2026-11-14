Push-Location $PSScriptRoot
try {
    $pyinstallerCommand = Get-Command pyinstaller -ErrorAction SilentlyContinue
    if ($pyinstallerCommand) {
        $pyinstallerPath = $pyinstallerCommand.Source
    }
    else {
        $localPyInstaller = Join-Path $PSScriptRoot ".venv\Scripts\pyinstaller.exe"
        if (Test-Path $localPyInstaller) {
            $pyinstallerPath = $localPyInstaller
        }
    }

    if (-not $pyinstallerPath) {
        throw "PyInstaller was not found. Activate the project's virtual environment or install PyInstaller first."
    }

    & $pyinstallerPath `
        --onefile `
        --name PrivvyCeeDev `
        --icon "assets\fingerprint.ico" `
        --collect-all textual `
        --add-data "src/css;src/css" `
        main.py

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
