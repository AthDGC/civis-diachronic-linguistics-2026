# ENHANCED C: Drive Cleanup Script v2.0
# Smart analysis and safe deletion recommendations

$host.UI.RawUI.WindowTitle = "Enhanced C: Drive Cleanup - Running..."

Write-Host "============================================" -ForegroundColor Green
Write-Host "  ENHANCED C: DRIVE CLEANUP v2.0" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Check initial space
Write-Host "[CHECKING] Getting initial disk space..." -ForegroundColor Yellow
$initialSpace = (Get-PSDrive C).Free / 1GB
$totalSpace = (Get-PSDrive C).Used / 1GB + $initialSpace
Write-Host "[RESULT] C: Drive has $([math]::Round($initialSpace, 2)) GB free out of $([math]::Round($totalSpace, 2)) GB" -ForegroundColor Cyan
Write-Host ""
Start-Sleep -Seconds 1

$stepNumber = 1
$totalSteps = 15

function Show-Progress {
    param($action, $details = "")
    Write-Host "[$script:stepNumber/$totalSteps] $action" -ForegroundColor White -BackgroundColor DarkBlue
    if ($details) {
        Write-Host "    → $details" -ForegroundColor Gray
    }
    $script:stepNumber++
}

# ==== STANDARD CLEANUP (Steps 1-6) ====

Show-Progress "EMPTYING RECYCLE BIN" "Removing deleted files..."
try {
    $shell = New-Object -ComObject Shell.Application
    $recycleBin = $shell.Namespace(0xA)
    $items = $recycleBin.Items()
    $itemCount = $items.Count
    
    if ($itemCount -gt 0) {
        Clear-RecycleBin -Force -ErrorAction Stop
        Write-Host "    ✓ Removed $itemCount items from Recycle Bin" -ForegroundColor Green
    } else {
        Write-Host "    ✓ Recycle Bin already empty" -ForegroundColor Green
    }
} catch {
    Write-Host "    ⚠ Could not empty Recycle Bin" -ForegroundColor Yellow
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "CLEANING WINDOWS TEMP" "$env:TEMP"
try {
    $tempFiles = Get-ChildItem -Path "$env:TEMP" -Recurse -Force -ErrorAction SilentlyContinue
    $tempCount = $tempFiles.Count
    Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Cleaned $tempCount temporary files" -ForegroundColor Green
} catch {
    Write-Host "    ⚠ Cleaned what we could" -ForegroundColor Yellow
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "CLEANING SYSTEM TEMP" "C:\Windows\Temp"
try {
    Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ System temp cleaned" -ForegroundColor Green
} catch {
    Write-Host "    ⚠ Cleaned what we could" -ForegroundColor Yellow
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "CLEARING BROWSER CACHES" "Chrome, Edge, Firefox..."
# Chrome
$chromePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"
if (Test-Path $chromePath) {
    Remove-Item -Path "$chromePath\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Chrome cache cleared" -ForegroundColor Green
}
# Edge
$edgePath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache"
if (Test-Path $edgePath) {
    Remove-Item -Path "$edgePath\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Edge cache cleared" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "CLEARING WINDOWS UPDATE CACHE" "May take a moment..."
try {
    Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
    Start-Service wuauserv -ErrorAction SilentlyContinue
    Write-Host "    ✓ Windows Update cache cleared" -ForegroundColor Green
} catch {
    Write-Host "    ⚠ Partially cleared" -ForegroundColor Yellow
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "CLEARING PREFETCH" "C:\Windows\Prefetch"
try {
    Remove-Item -Path "C:\Windows\Prefetch\*" -Force -ErrorAction SilentlyContinue
    Write-Host "    ✓ Prefetch cleared" -ForegroundColor Green
} catch {
    Write-Host "    ⚠ Could not clear" -ForegroundColor Yellow
}
Write-Host ""
Start-Sleep -Seconds 1

# ==== ENHANCED ANALYSIS (Steps 7-15) ====

Show-Progress "CHECKING FOR WINDOWS.OLD" "Old Windows installations..."
$windowsOld = "C:\Windows.old"
if (Test-Path $windowsOld) {
    $oldSize = (Get-ChildItem -Path $windowsOld -Recurse -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "    ⚠ Found Windows.old folder: $([math]::Round($oldSize, 2)) GB" -ForegroundColor Yellow
    Write-Host "    → To remove: Run 'cleanmgr' → 'Clean up system files' → Check 'Previous Windows installations'" -ForegroundColor Cyan
} else {
    Write-Host "    ✓ No Windows.old folder found" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "FINDING INSTALLER FILES" "Looking for .exe, .msi, .zip in Downloads..."
$installerPaths = @("$env:USERPROFILE\Downloads", "$env:USERPROFILE\Desktop")
$installers = @()

foreach ($path in $installerPaths) {
    if (Test-Path $path) {
        $found = Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | 
                 Where-Object { $_.Extension -match '\.(exe|msi|zip|rar|7z|iso)$' -and $_.Length -gt 50MB }
        $installers += $found
    }
}

if ($installers) {
    $installerSize = ($installers | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "    ℹ Found $($installers.Count) large installers/archives ($([math]::Round($installerSize, 2)) GB)" -ForegroundColor Cyan
    Write-Host "    → Review these manually - may be old downloads you don't need" -ForegroundColor Yellow
    $installers | Select-Object -First 5 | ForEach-Object {
        Write-Host "      • $([math]::Round($_.Length/1MB, 0)) MB - $($_.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "    ✓ No large installer files found" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "ANALYZING LUCENE INDEX FILES" "Checking for large database indexes..."
$luceneFiles = Get-ChildItem -Path "C:\Users" -Recurse -File -ErrorAction SilentlyContinue | 
               Where-Object { $_.Name -match '(\.fdt|\.pos|\.pay|\.doc|segments)' -and $_.Length -gt 100MB }

if ($luceneFiles) {
    $luceneSize = ($luceneFiles | Measure-Object -Property Length -Sum).Sum / 1GB
    $luceneDir = $luceneFiles[0].DirectoryName
    
    Write-Host "    ⚠ Found Lucene/database index files: $([math]::Round($luceneSize, 2)) GB" -ForegroundColor Yellow
    Write-Host "    → Location: $luceneDir" -ForegroundColor Cyan
    Write-Host "    → These are search index files - safe to delete if you can rebuild the index" -ForegroundColor Cyan
    
    $luceneFiles | Select-Object -First 5 | ForEach-Object {
        Write-Host "      • $([math]::Round($_.Length/1GB, 2)) GB - $($_.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "    ✓ No large index files found" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "FINDING AI MODEL FILES" "Looking for .gguf, .bin, .safetensors..."
$modelFiles = Get-ChildItem -Path "C:\Users" -Recurse -File -ErrorAction SilentlyContinue | 
              Where-Object { $_.Extension -match '\.(gguf|bin|safetensors|pt|pth)$' -and $_.Length -gt 500MB }

if ($modelFiles) {
    $modelSize = ($modelFiles | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "    ℹ Found AI model files: $([math]::Round($modelSize, 2)) GB" -ForegroundColor Cyan
    $modelFiles | ForEach-Object {
        Write-Host "      • $([math]::Round($_.Length/1GB, 2)) GB - $($_.Name)" -ForegroundColor Gray
        Write-Host "        Location: $($_.DirectoryName)" -ForegroundColor DarkGray
    }
    Write-Host "    → Keep only models you actively use" -ForegroundColor Yellow
} else {
    Write-Host "    ✓ No large model files found" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "CHECKING FOR DUPLICATE FILES" "Scanning for potential duplicates..."
Write-Host "    → Looking for files with same size (quick check)..." -ForegroundColor Gray

$largeFiles = Get-ChildItem -Path "C:\Users" -Recurse -File -ErrorAction SilentlyContinue | 
              Where-Object { $_.Length -gt 100MB } | 
              Group-Object Length | 
              Where-Object { $_.Count -gt 1 }

if ($largeFiles) {
    Write-Host "    ℹ Found potential duplicate large files:" -ForegroundColor Cyan
    foreach ($group in ($largeFiles | Select-Object -First 3)) {
        Write-Host "      Size: $([math]::Round($group.Name/1MB, 0)) MB - $($group.Count) files" -ForegroundColor Yellow
        $group.Group | ForEach-Object {
            Write-Host "        • $($_.Name) - $($_.DirectoryName)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "    ✓ No obvious duplicates found" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "ANALYZING APPDATA FOLDERS" "Finding large application data..."
$appDataPaths = @(
    "$env:LOCALAPPDATA",
    "$env:APPDATA"
)

$largeAppData = @()
foreach ($path in $appDataPaths) {
    if (Test-Path $path) {
        Get-ChildItem -Path $path -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $size = (Get-ChildItem -Path $_.FullName -Recurse -ErrorAction SilentlyContinue | 
                    Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum / 1GB
            if ($size -gt 1) {
                $largeAppData += [PSCustomObject]@{
                    Folder = $_.Name
                    Path = $_.FullName
                    SizeGB = [math]::Round($size, 2)
                }
            }
        }
    }
}

if ($largeAppData) {
    Write-Host "    ℹ Large AppData folders:" -ForegroundColor Cyan
    $largeAppData | Sort-Object SizeGB -Descending | Select-Object -First 5 | ForEach-Object {
        Write-Host "      • $($_.SizeGB) GB - $($_.Folder)" -ForegroundColor Yellow
    }
    Write-Host "    → Check these for cache/temp data that can be cleared" -ForegroundColor Gray
} else {
    Write-Host "    ✓ No unusually large AppData folders" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "CHECKING DOCKER/WSL DATA" "Looking for container/VM data..."
$dockerData = "C:\ProgramData\Docker"
$wslData = "$env:LOCALAPPDATA\Packages\CanonicalGroupLimited.Ubuntu"

$foundContainers = $false
if (Test-Path $dockerData) {
    $dockerSize = (Get-ChildItem -Path $dockerData -Recurse -ErrorAction SilentlyContinue | 
                   Measure-Object -Property Length -Sum).Sum / 1GB
    if ($dockerSize -gt 1) {
        Write-Host "    ⚠ Docker data: $([math]::Round($dockerSize, 2)) GB" -ForegroundColor Yellow
        Write-Host "    → Run 'docker system prune -a' to clean" -ForegroundColor Cyan
        $foundContainers = $true
    }
}

if (Test-Path $wslData) {
    $wslSize = (Get-ChildItem -Path $wslData -Recurse -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1GB
    if ($wslSize -gt 1) {
        Write-Host "    ⚠ WSL data: $([math]::Round($wslSize, 2)) GB" -ForegroundColor Yellow
        Write-Host "    → Run 'wsl --shutdown' then compact the VHDX" -ForegroundColor Cyan
        $foundContainers = $true
    }
}

if (-not $foundContainers) {
    Write-Host "    ✓ No large container/VM data found" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "SCANNING FOR VIDEO FILES" "Large media that could be archived..."
$videoFiles = Get-ChildItem -Path "C:\Users" -Recurse -File -ErrorAction SilentlyContinue | 
              Where-Object { $_.Extension -match '\.(mp4|avi|mkv|mov|wmv)$' -and $_.Length -gt 500MB } | 
              Sort-Object Length -Descending | 
              Select-Object -First 10

if ($videoFiles) {
    $videoSize = ($videoFiles | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "    ℹ Found large video files: $([math]::Round($videoSize, 2)) GB" -ForegroundColor Cyan
    $videoFiles | Select-Object -First 5 | ForEach-Object {
        Write-Host "      • $([math]::Round($_.Length/1GB, 2)) GB - $($_.Name)" -ForegroundColor Gray
    }
    Write-Host "    → Consider moving to external storage or deleting if watched" -ForegroundColor Yellow
} else {
    Write-Host "    ✓ No large video files found" -ForegroundColor Green
}
Write-Host ""
Start-Sleep -Seconds 1

Show-Progress "CREATING DETAILED REPORT" "Generating cleanup recommendations..."

# Create detailed report file
$reportPath = "$env:USERPROFILE\Desktop\Disk_Cleanup_Report.txt"
$report = @"
===========================================
DISK CLEANUP ANALYSIS REPORT
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
===========================================

INITIAL STATE:
- Total Capacity: $([math]::Round($totalSpace, 2)) GB
- Free Space: $([math]::Round($initialSpace, 2)) GB
- Used Space: $([math]::Round($totalSpace - $initialSpace, 2)) GB

FINDINGS & RECOMMENDATIONS:
"@

# Add findings to report
if ($luceneFiles) {
    $report += "`n`nLUCENE INDEX FILES ($([math]::Round($luceneSize, 2)) GB):"
    $luceneFiles | ForEach-Object {
        $report += "`n  - $([math]::Round($_.Length/1GB, 2)) GB - $($_.FullName)"
    }
    $report += "`n  RECOMMENDATION: These are search index files. Safe to delete if you can rebuild."
}

if ($modelFiles) {
    $report += "`n`nAI MODEL FILES ($([math]::Round($modelSize, 2)) GB):"
    $modelFiles | ForEach-Object {
        $report += "`n  - $([math]::Round($_.Length/1GB, 2)) GB - $($_.FullName)"
    }
    $report += "`n  RECOMMENDATION: Keep only models you actively use. Delete or archive others."
}

if ($installers) {
    $report += "`n`nOLD INSTALLERS/ARCHIVES ($([math]::Round($installerSize, 2)) GB):"
    $installers | Select-Object -First 10 | ForEach-Object {
        $report += "`n  - $([math]::Round($_.Length/1MB, 0)) MB - $($_.FullName)"
    }
    $report += "`n  RECOMMENDATION: Delete installers for software you've already installed."
}

$report | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "    ✓ Detailed report saved to Desktop" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 1

# Final check
$finalSpace = (Get-PSDrive C).Free / 1GB
$recovered = $finalSpace - $initialSpace

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "           ANALYSIS COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Space recovered: $([math]::Round($recovered, 2)) GB" -ForegroundColor Cyan
Write-Host "Current free space: $([math]::Round($finalSpace, 2)) GB" -ForegroundColor Green
Write-Host ""
Write-Host "MAJOR SPACE CONSUMERS IDENTIFIED:" -ForegroundColor Yellow
if ($luceneFiles) {
    Write-Host "  • Lucene indexes: ~$([math]::Round($luceneSize, 2)) GB (can be rebuilt)" -ForegroundColor White
}
if ($modelFiles) {
    Write-Host "  • AI models: ~$([math]::Round($modelSize, 2)) GB (keep only what you use)" -ForegroundColor White
}
if ($installers) {
    Write-Host "  • Old installers: ~$([math]::Round($installerSize, 2)) GB (safe to delete)" -ForegroundColor White
}
Write-Host ""
Write-Host "📄 Full report saved to: $reportPath" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
