# 导入消防知识文档到 RAG 服务
# PowerShell 版本（Windows 友好）

$ErrorActionPreference = "Stop"

# RAG 服务配置
$RAG_SERVICE_URL = "http://localhost:3000"

Write-Host "================================================================================"
Write-Host "消防知识文档导入工具"
Write-Host "================================================================================"
Write-Host ""

# 读取文档
$docFile = Join-Path $PSScriptRoot "..\data\knowledge_base\rag_documents.json"

if (!(Test-Path $docFile)) {
    Write-Host "[ERROR] 文档文件不存在: $docFile" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] 读取文档文件: $docFile"
$documents = Get-Content $docFile -Raw | ConvertFrom-Json

Write-Host "[OK] 找到 $($documents.Count) 个文档"
Write-Host ""

# 检查 RAG 服务
Write-Host "[INFO] 检查 RAG 服务..."
try {
    $health = Invoke-RestMethod -Uri "$RAG_SERVICE_URL/health" -Method GET -TimeoutSec 5
    if ($health.success) {
        Write-Host "[OK] RAG 服务健康"
    } else {
        Write-Host "[ERROR] RAG 服务不健康" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] 无法连接到 RAG 服务: $_" -ForegroundColor Red
    Write-Host "        请确保 RAG 服务运行在 $RAG_SERVICE_URL"
    exit 1
}

Write-Host ""

# 上传文档
Write-Host "[INFO] 开始导入文档..."
Write-Host "--------------------------------------------------------------------------------"

$successCount = 0
$errorCount = 0
$i = 0

foreach ($doc in $documents) {
    $i++
    $title = $doc.title
    $titleShort = if ($title.Length -gt 50) { $title.Substring(0, 50) + "..." } else { $title }
    
    Write-Host -NoNewline "[$i/$($documents.Count)] 上传: $titleShort... "
    
    try {
        # 构建 URL 参数
        $title_encoded = [System.Web.HttpUtility]::UrlEncode($doc.title)
        $content_encoded = [System.Web.HttpUtility]::UrlEncode($doc.content)
        
        $url = "$RAG_SERVICE_URL/documents?title=$title_encoded&content=$content_encoded"
        
        # 如果有 metadata，添加到 URL
        if ($doc.metadata) {
            $metadata_json = ($doc.metadata | ConvertTo-Json -Compress -Depth 10)
            $metadata_encoded = [System.Web.HttpUtility]::UrlEncode($metadata_json)
            $url += "&metadata=$metadata_encoded"
        }
        
        # 调用上传接口
        $result = Invoke-RestMethod -Uri $url -Method POST -TimeoutSec 30
        
        Write-Host "[OK]" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "[FAIL] - $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
    
    # 避免请求过快
    Start-Sleep -Milliseconds 100
}

Write-Host "--------------------------------------------------------------------------------"
Write-Host ""

# 打印统计信息
Write-Host "[STATS] 导入统计:"
Write-Host "  总计: $($documents.Count) 个文档"
Write-Host "  成功: $successCount 个" -ForegroundColor Green
Write-Host "  失败: $errorCount 个" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "White" })
Write-Host ""

# 检查导入后的统计信息
Write-Host "[INFO] 检查导入结果..."
try {
    $stats = Invoke-RestMethod -Uri "$RAG_SERVICE_URL/stats" -Method GET
    if ($stats.success) {
        $totalDocs = $stats.data.total_documents
        Write-Host "[OK] RAG 数据库现有 $totalDocs 个文档" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] 无法获取统计信息: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================"

if ($errorCount -eq 0) {
    Write-Host "[SUCCESS] 所有文档导入成功！" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[WARN] 导入完成，但有 $errorCount 个文档失败" -ForegroundColor Yellow
    exit 1
}

