[CmdletBinding()]
param(
    [ValidateSet("agent", "gateway", "web", "backend", "all", "infra", "status", "down", "clean")]
    [string]$Target
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$ComposeFiles = @(
    "--file", (Join-Path $ProjectRoot "docker-compose.yml"),
    "--file", (Join-Path $ProjectRoot "docker-compose.dev.yml")
)
$DataRoot = if ($env:QUELYRA_DATA_ROOT) { $env:QUELYRA_DATA_ROOT } else { "D:\data\quelyra" }

function Invoke-QuelyraCompose {
    param([string[]]$Arguments)

    & docker compose @ComposeFiles @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Quelyra Compose 命令执行失败，退出码：$LASTEXITCODE"
    }
}

function Test-QuelyraDocker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "未找到 Docker，请先安装并启动 Docker Desktop。"
    }

    & docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker daemon 不可用，请先启动 Docker Desktop。"
    }
}

function Initialize-QuelyraData {
    foreach ($directory in @("postgres", "redis")) {
        $path = Join-Path $DataRoot $directory
        if (-not (Test-Path -LiteralPath $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
            Write-Host "[Quelyra] 已创建数据目录：$path"
        }
    }
}

function Start-QuelyraServices {
    param(
        [string]$Label,
        [string[]]$Services
    )

    Initialize-QuelyraData
    Write-Host "[Quelyra] 正在启动 $Label..."
    Invoke-QuelyraCompose -Arguments (@("up", "--detach", "--build") + $Services)
    Write-Host "[Quelyra] $Label 已启动。"
    Invoke-QuelyraCompose -Arguments @("ps")
}

function Read-QuelyraTarget {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "          Quelyra 开发环境"
    Write-Host "========================================"
    Write-Host "1. 启动 Agent API"
    Write-Host "2. 启动 Query Gateway"
    Write-Host "3. 启动 Web 工作台"
    Write-Host "4. 启动后端服务"
    Write-Host "5. 启动完整 Quelyra"
    Write-Host "6. 只启动基础设施"
    Write-Host "7. 查看服务状态"
    Write-Host "8. 停止全部服务"
    Write-Host "9. 清理容器和本地应用镜像（保留数据）"
    Write-Host "0. 退出"
    Write-Host ""

    $choice = Read-Host "请选择"
    return @{
        "1" = "agent"
        "2" = "gateway"
        "3" = "web"
        "4" = "backend"
        "5" = "all"
        "6" = "infra"
        "7" = "status"
        "8" = "down"
        "9" = "clean"
        "0" = "exit"
    }[$choice]
}

if (-not $Target) {
    $Target = Read-QuelyraTarget
    if (-not $Target) {
        throw "无效选项。"
    }
}

if ($Target -eq "exit") {
    return
}

Test-QuelyraDocker

switch ($Target) {
    "agent" {
        Start-QuelyraServices -Label "Agent API" -Services @("postgres", "redis", "agent-api")
    }
    "gateway" {
        Start-QuelyraServices -Label "Query Gateway" -Services @("postgres", "redis", "query-gateway")
    }
    "web" {
        Start-QuelyraServices -Label "Web 工作台" -Services @("web")
    }
    "backend" {
        Start-QuelyraServices -Label "后端服务" -Services @("postgres", "redis", "agent-api", "query-gateway")
    }
    "all" {
        Start-QuelyraServices -Label "完整 Quelyra" -Services @("postgres", "redis", "agent-api", "query-gateway", "web")
    }
    "infra" {
        Start-QuelyraServices -Label "基础设施" -Services @("postgres", "redis")
    }
    "status" {
        Invoke-QuelyraCompose -Arguments @("ps")
    }
    "down" {
        Write-Host "[Quelyra] 正在停止全部服务，宿主机数据将保留。"
        Invoke-QuelyraCompose -Arguments @("down", "--remove-orphans")
    }
    "clean" {
        Write-Warning "此操作将删除 Quelyra 容器和本地构建的应用镜像，但保留 $DataRoot 中的数据。"
        $confirmation = Read-Host "请输入 CLEAN 确认"
        if ($confirmation -ne "CLEAN") {
            Write-Host "[Quelyra] 已取消清理。"
            return
        }
        Invoke-QuelyraCompose -Arguments @("down", "--remove-orphans", "--rmi", "local")
        Write-Host "[Quelyra] 清理完成，宿主机数据仍保存在 $DataRoot。"
    }
}
