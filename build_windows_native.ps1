$ErrorActionPreference = "Stop"

python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if (-not (Test-Path "avatars")) {
    New-Item -ItemType Directory -Path "avatars" | Out-Null
}

if (-not (Test-Path "settings.json")) {
    @{
        camera_index = 0
        target_fps = 30
        pose_filter_alpha = 0.35
        gpu_enabled = $true
        enable_preview = $false
        auto_detect = $true
        auto_start = $true
        minimize_to_tray = $true
        avatar_dir = "avatars"
    } | ConvertTo-Json | Set-Content -Path "settings.json"
}

pyinstaller face_swap_avatar_gui.spec

Write-Host ""
Write-Host "Build complete. Find your app in:"
Write-Host "dist\FaceSwapAvatar\FaceSwapAvatar.exe"
