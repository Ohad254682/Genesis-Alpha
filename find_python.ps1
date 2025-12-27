# PowerShell script to find Python installations
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Finding Python Installations..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$pythonPaths = @()

# Check common installation locations
$searchPaths = @(
    "$env:LOCALAPPDATA\Programs\Python",
    "$env:PROGRAMFILES\Python*",
    "$env:PROGRAMFILES(X86)\Python*",
    "$env:USERPROFILE\AppData\Local\Programs\Python",
    "C:\Python*",
    "$env:USERPROFILE\anaconda*",
    "$env:USERPROFILE\miniconda*"
)

Write-Host "Searching for Python installations..." -ForegroundColor Yellow

foreach ($path in $searchPaths) {
    $found = Get-ChildItem -Path $path -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue -Depth 3
    if ($found) {
        foreach ($python in $found) {
            $version = & $python.FullName --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $version -notlike "*was not found*") {
                $pythonPaths += @{
                    Path = $python.FullName
                    Version = $version
                    Directory = $python.DirectoryName
                }
                Write-Host "  Found: $($python.FullName)" -ForegroundColor Green
                Write-Host "    Version: $version" -ForegroundColor Gray
            }
        }
    }
}

Write-Host ""
if ($pythonPaths.Count -eq 0) {
    Write-Host "No Python installations found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from one of these sources:" -ForegroundColor Yellow
    Write-Host "  1. https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "  2. Microsoft Store (search for 'Python')" -ForegroundColor Cyan
    Write-Host "  3. Anaconda: https://www.anaconda.com/products/distribution" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "IMPORTANT: During installation, check 'Add Python to PATH'" -ForegroundColor Yellow
} else {
    Write-Host "Found $($pythonPaths.Count) Python installation(s):" -ForegroundColor Green
    Write-Host ""
    for ($i = 0; $i -lt $pythonPaths.Count; $i++) {
        $p = $pythonPaths[$i]
        Write-Host "[$($i+1)] $($p.Version)" -ForegroundColor Cyan
        Write-Host "    Path: $($p.Path)" -ForegroundColor Gray
        Write-Host "    Directory: $($p.Directory)" -ForegroundColor Gray
        Write-Host ""
    }
    
    # Create a batch file that uses the first Python found
    $firstPython = $pythonPaths[0].Path
    $batContent = @"
@echo off
echo Using Python: $firstPython
echo.
"$firstPython" -m streamlit run app/main.py
pause
"@
    $batContent | Out-File -FilePath "run_with_found_python.bat" -Encoding ASCII
    Write-Host "Created 'run_with_found_python.bat' to use the first Python found." -ForegroundColor Green
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")








