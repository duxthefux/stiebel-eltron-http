# Run mypy from inside custom_components to avoid duplicate-module errors.
# Usage: Open PowerShell in the repo root and run:
#  .\custom_components\run_mypy.ps1

$python = "C:/Users/Feindt/AppData/Local/Microsoft/WindowsApps/python3.13.exe"
Push-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
try {
    if ($args.Count -gt 0) {
        # Run mypy on provided paths
        & $python -m mypy --show-error-codes --config-file mypy.ini @args
    } else {
        # By default only run the focused files we recently tightened to avoid
        # surfacing unrelated typing issues in other modules.
        & $python -m mypy --show-error-codes --config-file mypy.ini stiebel_eltron_http/parsing.py stiebel_eltron_http/scraper.py
    }
} finally {
    Pop-Location
}
