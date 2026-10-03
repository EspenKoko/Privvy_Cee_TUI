cd C:\Development\Projects\Tech_Accelerator_2026\Privvy_Cee_TUI
pyinstaller `
    --onefile `
    --name PrivvyCeeTUI `
    --icon "assets\fingerprint.ico" `
    --collect-all textual `
    --add-data "src/css;src/css" main.py