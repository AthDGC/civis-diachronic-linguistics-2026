# MOVE Large Files to Z: Drive (FREE UP C: SPACE)
# This will MOVE files (not copy) to free up 52+ GB

$host.UI.RawUI.WindowTitle = "Moving Files to Z: Drive..."

Write-Host "============================================" -ForegroundColor Green
Write-Host "  MOVING FILES TO Z: DRIVE" -ForegroundColor Green
Write-Host "  (This will FREE UP space on C:)" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Check Z: drive exists
if (-not (Test-Path "Z:\")) {
    Write-Host "ERROR: Z: drive not found!" -ForegroundColor Red
    Write-Host "Please make sure your external drive is connected and assigned to Z:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Check Z: drive has enough space
$zDrive = Get-PSDrive Z
$zFreeSpace = $zDrive.Free / 1GB
Write-Host "[CHECK] Z: drive has $([math]::Round($zFreeSpace, 2)) GB free" -ForegroundColor Cyan

if ($zFreeSpace -lt 55) {
    Write-Host "WARNING: Z: drive may not have enough space (need ~55 GB)" -ForegroundColor Yellow
    Write-Host "Do you want to continue anyway? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -ne 'Y' -and $response -ne 'y') {
        Write-Host "Operation cancelled." -ForegroundColor Red
        exit
    }
}
Write-Host ""

# Initial C: space
$initialCSpace = (Get-PSDrive C).Free / 1GB
Write-Host "[INITIAL] C: drive free space: $([math]::Round($initialCSpace, 2)) GB" -ForegroundColor Yellow
Write-Host ""

$totalMoved = 0
$stepNumber = 1

function Move-WithProgress {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Description
    )
    
    Write-Host "[$script:stepNumber] MOVING: $Description" -ForegroundColor White -BackgroundColor DarkBlue
    Write-Host "    From: $Source" -ForegroundColor Gray
    Write-Host "    To:   $Destination" -ForegroundColor Gray
    
    if (-not (Test-Path $Source)) {
        Write-Host "    ⚠ Source not found, skipping" -ForegroundColor Yellow
        $script:stepNumber++
        return 0
    }
    
    try {
        # Calculate size before moving
        $size = (Get-ChildItem -Path $Source -Recurse -File -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum / 1GB
        
        # Create destination directory if it doesn't exist
        $destDir = Split-Path -Parent $Destination
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        # Move the files
        Write-Host "    → Moving $([math]::Round($size, 2)) GB..." -ForegroundColor Cyan
        Move-Item -Path $Source -Destination $Destination -Force -ErrorAction Stop
        
        Write-Host "    ✓ Successfully moved $([math]::Round($size, 2)) GB" -ForegroundColor Green
        $script:stepNumber++
        return $size
    }
    catch {
        Write-Host "    ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:stepNumber++
        return 0
    }
    
    Write-Host ""
}

# Create organized structure on Z:
Write-Host "[SETUP] Creating organized folders on Z:..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "Z:\LancsBoxX_Data" -Force | Out-Null
New-Item -ItemType Directory -Path "Z:\AI_Models" -Force | Out-Null
New-Item -ItemType Directory -Path "Z:\AI_Models\LM_Studio" -Force | Out-Null
New-Item -ItemType Directory -Path "Z:\AI_Models\HuggingFace" -Force | Out-Null
Write-Host "    ✓ Folders created" -ForegroundColor Green
Write-Host ""

# === MOVE LUCENE INDEXES (36 GB) ===
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  MOVING LUCENE INDEXES (36 GB)" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$moved = Move-WithProgress `
    -Source "C:\Users\nlavi\LancsBoxX\corpora\Hansard\lucene" `
    -Destination "Z:\LancsBoxX_Data\Hansard_lucene" `
    -Description "Hansard Lucene Indexes"
$totalMoved += $moved

# === MOVE PUNCTUATION-NUMBERS.BIN (7.26 GB) ===
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  MOVING LANCSBOX LANGUAGE MODEL (7 GB)" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$moved = Move-WithProgress `
    -Source "C:\Users\nlavi\LancsBoxX\corpora\Hansard\punctuation-numbers.bin" `
    -Destination "Z:\LancsBoxX_Data\punctuation-numbers.bin" `
    -Description "LancsBox Language Model"
$totalMoved += $moved

# === MOVE LM STUDIO MODELS (8.6 GB) ===
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  MOVING LM STUDIO MODELS (8.6 GB)" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$moved = Move-WithProgress `
    -Source "C:\Users\nlavi\.lmstudio\models\lmstudio-community\Meta-Llama-3.1-8B-Instruct-GGUF" `
    -Destination "Z:\AI_Models\LM_Studio\Meta-Llama-3.1-8B-Instruct-GGUF" `
    -Description "Llama 3.1 Model"
$totalMoved += $moved

$moved = Move-WithProgress `
    -Source "C:\Users\nlavi\.lmstudio\models\lmstudio-community\Mistral-7B-Instruct-v0.3-GGUF" `
    -Destination "Z:\AI_Models\LM_Studio\Mistral-7B-Instruct-v0.3-GGUF" `
    -Description "Mistral Model"
$totalMoved += $moved

# === MOVE HUGGINGFACE CACHE (0.5 GB) ===
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  MOVING HUGGINGFACE MODELS (0.5 GB)" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$moved = Move-WithProgress `
    -Source "C:\Users\nlavi\.cache\huggingface\hub\models--gpt2" `
    -Destination "Z:\AI_Models\HuggingFace\models--gpt2" `
    -Description "GPT-2 Model"
$totalMoved += $moved

# === FINAL SUMMARY ===
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "           MIGRATION COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

$finalCSpace = (Get-PSDrive C).Free / 1GB
$spaceFreed = $finalCSpace - $initialCSpace

Write-Host "RESULTS:" -ForegroundColor Cyan
Write-Host "  Initial C: free space: $([math]::Round($initialCSpace, 2)) GB" -ForegroundColor Yellow
Write-Host "  Final C: free space:   $([math]::Round($finalCSpace, 2)) GB" -ForegroundColor Green
Write-Host "  Space freed:           $([math]::Round($spaceFreed, 2)) GB" -ForegroundColor White -BackgroundColor Green
Write-Host "  Data moved:            $([math]::Round($totalMoved, 2)) GB" -ForegroundColor Cyan
Write-Host ""

Write-Host "FILES NOW ON Z: DRIVE:" -ForegroundColor Yellow
Write-Host "  Z:\LancsBoxX_Data\Hansard_lucene\" -ForegroundColor White
Write-Host "  Z:\LancsBoxX_Data\punctuation-numbers.bin" -ForegroundColor White
Write-Host "  Z:\AI_Models\LM_Studio\Meta-Llama-3.1-8B-Instruct-GGUF\" -ForegroundColor White
Write-Host "  Z:\AI_Models\LM_Studio\Mistral-7B-Instruct-v0.3-GGUF\" -ForegroundColor White
Write-Host "  Z:\AI_Models\HuggingFace\models--gpt2\" -ForegroundColor White
Write-Host ""

Write-Host "IMPORTANT NOTES:" -ForegroundColor Yellow
Write-Host "  1. LancsBoxX will need to re-index the Hansard corpus" -ForegroundColor Gray
Write-Host "  2. LM Studio: Update model paths to Z:\AI_Models\LM_Studio\" -ForegroundColor Gray
Write-Host "  3. For HuggingFace: Set HF_HOME=Z:\AI_Models\HuggingFace" -ForegroundColor Gray
Write-Host "  4. Keep Z: drive connected when using these applications" -ForegroundColor Gray
Write-Host ""

# Create a reference file
$referenceFile = "Z:\MOVED_FROM_C_DRIVE.txt"
$reference = @"
Files moved from C: drive on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Total space freed: $([math]::Round($spaceFreed, 2)) GB

ORIGINAL LOCATIONS:
- C:\Users\nlavi\LancsBoxX\corpora\Hansard\lucene\
- C:\Users\nlavi\LancsBoxX\corpora\Hansard\punctuation-numbers.bin
- C:\Users\nlavi\.lmstudio\models\lmstudio-community\Meta-Llama-3.1-8B-Instruct-GGUF\
- C:\Users\nlavi\.lmstudio\models\lmstudio-community\Mistral-7B-Instruct-v0.3-GGUF\
- C:\Users\nlavi\.cache\huggingface\hub\models--gpt2\

NEW LOCATIONS:
- Z:\LancsBoxX_Data\Hansard_lucene\
- Z:\LancsBoxX_Data\punctuation-numbers.bin
- Z:\AI_Models\LM_Studio\Meta-Llama-3.1-8B-Instruct-GGUF\
- Z:\AI_Models\LM_Studio\Mistral-7B-Instruct-v0.3-GGUF\
- Z:\AI_Models\HuggingFace\models--gpt2\
"@

$reference | Out-File -FilePath $referenceFile -Encoding UTF8
Write-Host "📄 Reference file created: $referenceFile" -ForegroundColor Magenta
Write-Host ""

Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
