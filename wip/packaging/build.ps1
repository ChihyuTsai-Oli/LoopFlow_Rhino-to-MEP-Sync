# Build a local LoopFlow R2M yak (registers command names; not a public Package Manager release).
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = (Resolve-Path (Join-Path $Here "..\..")).Path
$Wip = Join-Path $Repo "wip"
$Build = Join-Path $Here "build"
$Prepared = Join-Path $Build "LoopFlow_R2M.prepared.rhproj"
$RhinoCode = "C:\Program Files\Rhino 8\System\RhinoCode.exe"
$Yak = "C:\Program Files\Rhino 8\System\Yak.exe"
$ProductRui = Join-Path $Wip "docs\toolbar\LoopFlow_R2M.rui"
$IconSrc = Join-Path $Wip "docs\toolbar\icon.png"
$Version = "1.0.0"

if (-not (Test-Path $RhinoCode)) { throw "RhinoCode.exe not found" }
if (-not (Test-Path $Yak)) { throw "Yak.exe not found" }
if (-not (Test-Path $ProductRui)) { throw "LoopFlow_R2M.rui not found" }
if (-not (Test-Path $IconSrc)) { throw "icon.png not found" }

Set-Location $Here
python generate_commands.py
if ($LASTEXITCODE -ne 0) { throw "generate_commands.py failed" }

New-Item -ItemType Directory -Force -Path $Build | Out-Null
python prepare_rhproj.py (Join-Path $Here "LoopFlow_R2M.rhproj") $Prepared
if ($LASTEXITCODE -ne 0) { throw "prepare_rhproj.py failed" }

& $RhinoCode project build $Prepared --buildversion $Version --buildtarget 8.* --buildpath $Build
if ($LASTEXITCODE -ne 0) { throw "RhinoCode project build failed" }

$Stage = Get-ChildItem -Path $Build -Recurse -Filter "LoopFlow_R2M.rhp" | Select-Object -First 1
if (-not $Stage) { throw "RhinoCode did not produce LoopFlow_R2M.rhp" }
$StageDir = $Stage.Directory.FullName

$Lib = Join-Path $StageDir "lib"
if (Test-Path $Lib) { Remove-Item $Lib -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Lib | Out-Null
Copy-Item -Recurse (Join-Path $Wip "src\loopflow_r2m") (Join-Path $Lib "loopflow_r2m")
Get-ChildItem (Join-Path $Lib "loopflow_r2m") -Recurse -Directory -Filter "__pycache__" |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

$GeneratedSrc = Join-Path $StageDir "src"
if (Test-Path $GeneratedSrc) { Remove-Item $GeneratedSrc -Force -Recurse }

$vendorSrc = Join-Path $Wip ".vendor\py39"
if (-not (Test-Path $vendorSrc)) { throw "missing vendor cache: $vendorSrc" }
$vendorRoot = Join-Path $StageDir "vendor"
$vendorDst = Join-Path $vendorRoot "py39"
if (Test-Path $vendorRoot) { Remove-Item $vendorRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path $vendorDst | Out-Null
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& robocopy.exe $vendorSrc $vendorDst /E /XD __pycache__ /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
$robo = $LASTEXITCODE
$ErrorActionPreference = $prevEap
if ($robo -ge 8) { throw "robocopy vendor failed: $robo" }

$RuiPath = Join-Path $StageDir "LoopFlow_R2M.rui"
if (Test-Path $RuiPath) { Remove-Item $RuiPath -Force }
Copy-Item -Force $ProductRui $RuiPath
$ruiText = Get-Content $RuiPath -Raw -Encoding UTF8
if ($ruiText -notmatch "_RMOpen") { throw "RUI missing ! _RMOpen" }
if ($ruiText -notmatch "tool_bar_group") { throw "RUI missing tool_bar_group" }

$DocsDst = Join-Path $StageDir "docs"
if (Test-Path $DocsDst) { Remove-Item $DocsDst -Recurse -Force }
Copy-Item (Join-Path $Repo "docs") $DocsDst -Recurse -Force
Copy-Item (Join-Path $Repo "LICENSE") (Join-Path $StageDir "LICENSE") -Force
Copy-Item -Force $IconSrc (Join-Path $StageDir "icon.png")
Copy-Item -Force (Join-Path $Here "manifest.yml") (Join-Path $StageDir "manifest.yml")

$notice = Join-Path $StageDir "THIRD_PARTY_IFCOPENSHELL.txt"
Set-Content -Path $notice -Encoding UTF8 -Value "IfcOpenShell 0.8.4.post1 is bundled under vendor/py39 (LGPL)."

Get-ChildItem $StageDir -Filter "*.yak" | Remove-Item -Force

Push-Location $StageDir
try {
    & $Yak build --platform win
    if ($LASTEXITCODE -ne 0) { throw "yak build failed" }
    $Built = Get-ChildItem *.yak | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $Built) { throw "yak build produced no .yak" }
    Copy-Item -Force $Built.FullName $Build
    $out = Join-Path $Build $Built.Name
    Write-Host "built $out"
} finally {
    Pop-Location
}
