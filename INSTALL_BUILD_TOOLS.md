# Installing Microsoft Visual C++ Build Tools

The following packages require C++ build tools to compile:
- cvxpy (for portfolio optimization)
- ecos
- osqp

## Quick Installation Steps

1. **Download the Installer**:
   - Visit: https://visualstudio.microsoft.com/downloads/
   - Scroll to "Tools for Visual Studio" section
   - Click "Download" under "Build Tools for Visual Studio 2022" (or latest version)

2. **Run the Installer**:
   - Double-click `vs_BuildTools.exe`
   - When prompted, select "Desktop development with C++" workload
   - Click "Install"

3. **After Installation**:
   - Restart your computer (recommended)
   - Open a new terminal/command prompt
   - Run: `python -m pip install -r requirements.txt`

## Alternative: Install via Command Line (Advanced)

If you prefer command-line installation, you can download and run:

```powershell
# Download the installer
Invoke-WebRequest -Uri "https://aka.ms/vs/17/release/vs_buildtools.exe" -OutFile "$env:TEMP\vs_buildtools.exe"

# Run installer (requires admin privileges)
Start-Process -FilePath "$env:TEMP\vs_buildtools.exe" -ArgumentList "--quiet", "--wait", "--add", "Microsoft.VisualStudio.Workload.VCTools" -Verb RunAs
```

**Note**: The command-line method requires administrator privileges and may take 10-20 minutes.

## Verify Installation

After installation, verify it worked:

```powershell
python -m pip install cvxpy
```

If this succeeds, the build tools are properly installed.

## Skip Portfolio Optimization (Temporary Workaround)

If you don't need portfolio optimization features immediately, you can skip installing PyPortfolioOpt and cvxpy. The app will work for:
- Stock analysis
- KPI calculations
- Technical indicators
- AI recommendations

But portfolio optimization features will be unavailable.







