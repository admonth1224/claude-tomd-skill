# tomd skill installer (Windows / PowerShell)
# Usage:  ./install.ps1
$ErrorActionPreference = "Stop"

Write-Host "==> tomd 스킬 설치 시작" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$src      = Join-Path $repoRoot "tomd"
$dest     = Join-Path $env:USERPROFILE ".claude\skills\tomd"

# 1) Python 확인
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) {
    Write-Host "Python을 찾을 수 없습니다. https://www.python.org 에서 설치 후 다시 실행하세요." -ForegroundColor Red
    exit 1
}

# 2) 의존성 설치
Write-Host "==> Python 의존성 설치 중 (markitdown[all], pyhwp)..." -ForegroundColor Cyan
& $py.Source -m pip install -r (Join-Path $repoRoot "requirements.txt")

# 3) 스킬 복사
Write-Host "==> 스킬 복사: $dest" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item -Path (Join-Path $src "*") -Destination $dest -Recurse -Force

Write-Host ""
Write-Host "✅ 설치 완료!" -ForegroundColor Green
Write-Host "   Claude Code에서 다음처럼 사용하세요:  /tomd <파일명>" -ForegroundColor Green
Write-Host "   (Claude Code가 실행 중이면 한 번 재시작하면 /tomd 가 인식됩니다.)"
