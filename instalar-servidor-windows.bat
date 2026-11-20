@echo off
rem Preparar um computador Windows com placa grafica para ser o SERVIDOR do
rem modelo: os portateis da sala ligam-se a ele pelo OpenCode.
rem
rem Uma vez por computador, com uma conta de administrador (a mesma conta
rem que vai estar ligada durante as sessoes do clube):
rem
rem   - Duplo clique. Pede autorizacao de administrador e pergunta o modelo.
rem   - Ou, numa linha de comandos:  instalar-servidor-windows.bat qwen2.5:7b
rem
rem O que faz:
rem   1. instala o Ollama, se ainda nao existir
rem   2. poe o Ollama a aceitar ligacoes da rede (OLLAMA_HOST=0.0.0.0)
rem   3. abre a porta 11434 na firewall do Windows
rem   4. descarrega o modelo
rem   5. mostra o endereco deste computador e o comando a correr nos portateis
rem
rem Pode correr-se outra vez sem estragar nada (para trocar de modelo, por
rem exemplo).
rem
rem O modelo tem de caber na memoria da placa grafica. Numa placa de 8 GB
rem cabe um modelo de 7 ou 8 mil milhoes de parametros (qwen2.5:7b); um de 20
rem (gpt-oss:20b) ja nao cabe e fica muito lento.
rem
rem Este ficheiro tem de ficar com fins de linha CRLF (ver .gitattributes).
rem Dai para baixo de PS-INICIO e PowerShell: o cmd nunca la chega.

setlocal
set "SELF=%~f0"
set "MODELO_PEDIDO=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s = Get-Content -LiteralPath $env:SELF -Raw; $i = $s.LastIndexOf('#PS-INICIO'); Invoke-Expression $s.Substring($i)"
echo.
pause
exit /b

#PS-INICIO
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$porta = 11434
$contexto = 16384
$regra = 'Ollama (Clube de Codigo)'
$modelo = $env:MODELO_PEDIDO

function Procurar-Ollama {
    $cmd = Get-Command ollama -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $p = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
    if (Test-Path $p) { return $p }
    return $null
}

function Ollama-Responde {
    try {
        Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 "http://127.0.0.1:${porta}/api/version" | Out-Null
        return $true
    } catch {
        return $false
    }
}

try {
    # Sem administrador nao se mexe na firewall: pede-se a autorizacao e
    # corre-se outra vez, ja com ela.
    $eu = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $eu.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host 'A pedir autorizacao de administrador...'
        if ($modelo) {
            Start-Process -FilePath $env:SELF -ArgumentList $modelo -Verb RunAs
        } else {
            Start-Process -FilePath $env:SELF -Verb RunAs
        }
        return
    }

    if (-not $modelo) {
        $resposta = Read-Host 'Modelo a instalar (Enter para qwen2.5:7b)'
        if ($resposta) { $modelo = $resposta.Trim() } else { $modelo = 'qwen2.5:7b' }
    }

    Write-Host '==> 1/5  Ollama'
    $ollama = Procurar-Ollama
    if ($ollama) {
        Write-Host "    Ja esta instalado: $ollama"
    } else {
        $instalador = Join-Path $env:TEMP 'OllamaSetup.exe'
        Write-Host '    A descarregar o instalador (mais de 1 GB)...'
        & curl.exe -fL --progress-bar -o $instalador 'https://ollama.com/download/OllamaSetup.exe'
        if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel descarregar o Ollama. Ha internet?' }
        Write-Host '    A instalar...'
        $p = Start-Process -FilePath $instalador -ArgumentList '/VERYSILENT', '/NORESTART' -PassThru
        $p.WaitForExit()
        $ollama = Procurar-Ollama
        if (-not $ollama) { throw 'O Ollama nao ficou instalado. Instala-o a mao a partir de ollama.com/download e corre isto outra vez.' }
    }

    Write-Host '==> 2/5  Aceitar ligacoes da rede'
    # Para o computador todo, e tambem para este processo, que e quem vai
    # arrancar o Ollama a seguir.
    $definicoes = @{
        OLLAMA_HOST           = '0.0.0.0'
        OLLAMA_CONTEXT_LENGTH = "$contexto"
        OLLAMA_KEEP_ALIVE     = '2h'
    }
    foreach ($nome in $definicoes.Keys) {
        [Environment]::SetEnvironmentVariable($nome, $definicoes[$nome], 'Machine')
        Set-Item -Path "Env:$nome" -Value $definicoes[$nome]
    }

    Write-Host "==> 3/5  Abrir a porta $porta na firewall"
    Get-NetFirewallRule -DisplayName $regra -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    New-NetFirewallRule -DisplayName $regra -Direction Inbound -Protocol TCP -LocalPort $porta -Action Allow | Out-Null

    Write-Host '    A reiniciar o Ollama para ele ler as definicoes novas...'
    Get-Process -Name 'ollama app', 'ollama' -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    $app = Join-Path (Split-Path $ollama) 'ollama app.exe'
    if (Test-Path $app) {
        Start-Process -FilePath $app
    } else {
        Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
    }
    $pronto = $false
    foreach ($tentativa in 1..60) {
        if (Ollama-Responde) { $pronto = $true; break }
        Start-Sleep -Seconds 1
    }
    if (-not $pronto) {
        # A aplicacao da bandeja nem sempre arranca o servidor sozinha.
        Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
        foreach ($tentativa in 1..30) {
            if (Ollama-Responde) { $pronto = $true; break }
            Start-Sleep -Seconds 1
        }
    }
    if (-not $pronto) { throw 'O Ollama nao responde. Abre-o a mao pelo menu Iniciar e corre isto outra vez.' }

    Write-Host "==> 4/5  Descarregar o modelo $modelo"
    & $ollama pull $modelo
    if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel descarregar o modelo $modelo. O nome esta certo?" }

    $corpo = @{ model = $modelo } | ConvertTo-Json
    $info = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:${porta}/api/show" -Body $corpo -ContentType 'application/json'
    if ($info.capabilities -notcontains 'tools') {
        Write-Host "AVISO: o modelo $modelo nao sabe usar ferramentas. O OpenCode vai"
        Write-Host '       conversar mas nao vai conseguir alterar ficheiros.'
    }

    Write-Host '    A carregar o modelo para a memoria (primeira pergunta)...'
    & $ollama run $modelo 'Responde so: ola' | Out-Null
    Write-Host '    Onde ficou o modelo (100% GPU e o ideal; CPU/GPU e mais lento):'
    & $ollama ps

    Write-Host '==> 5/5  Endereco deste computador'
    $ip = Get-NetIPConfiguration |
        Where-Object { $_.IPv4DefaultGateway -and $_.NetAdapter.Status -eq 'Up' } |
        ForEach-Object { $_.IPv4Address.IPAddress } |
        Select-Object -First 1
    if (-not $ip) { throw 'Este computador nao parece estar ligado a uma rede.' }
    try {
        Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 "http://${ip}:${porta}/api/version" | Out-Null
    } catch {
        throw "O Ollama responde aqui dentro mas nao em ${ip}:${porta}. Reinicia o computador e corre isto outra vez."
    }

    Write-Host ''
    Write-Host 'Pronto. Este computador e agora o servidor do modelo.'
    Write-Host ''
    Write-Host 'Em cada portatil, com a conta de administrador:'
    Write-Host ''
    Write-Host "    sudo bash mudar-modelo.sh $modelo http://${ip}:${porta}"
    Write-Host ''
    Write-Host 'Para o botao "Pedir ajuda" da Oficina, junta esta linha ao ficheiro'
    Write-Host 'oficina/servidores.txt. Com o nome do computador, que nao muda:'
    Write-Host ''
    Write-Host "    http://$($env:COMPUTERNAME.ToLower()).local:${porta}"
    Write-Host ''
    Write-Host 'Se os portateis nao derem com o nome, usa o endereco (pode mudar ao'
    Write-Host 'reiniciar):'
    Write-Host ''
    Write-Host "    http://${ip}:${porta}"
    Write-Host ''
    Write-Host 'A lembrar:'
    Write-Host '  - Este computador tem de estar ligado, com a sessao iniciada e sem'
    Write-Host '    suspender, enquanto os alunos trabalham.'
    Write-Host '  - Se o endereco mudar (acontece depois de reiniciar), corre isto'
    Write-Host '    outra vez para ver o novo e repete o comando nos portateis.'
} catch {
    Write-Host ''
    Write-Host "ERRO: $($_.Exception.Message)"
}
