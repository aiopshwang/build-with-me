# Python-free static server for Windows (PowerShell 5.1 compatible).
# Usage: powershell -File serve.ps1 <dir> [port]   |   powershell -File serve.ps1 <dir> -Stop
param([string]$Root = ".", [int]$Port = 0, [switch]$Stop)
$Root = (Resolve-Path $Root).Path.TrimEnd([IO.Path]::DirectorySeparatorChar)
$statePath = Join-Path $Root ".bwm\serve.json"
if ($Stop) {
  if (Test-Path $statePath) {
    try { $state = Get-Content $statePath -Raw | ConvertFrom-Json } catch { $state = $null }
    if ($state -and $state.pid) { try { Stop-Process -Id $state.pid -Force -ErrorAction Stop } catch {} }
    Remove-Item $statePath -Force -ErrorAction SilentlyContinue
    Write-Output "STOPPED"
  } else {
    Write-Output "NOT_RUNNING"
  }
  exit 0
}
if ($Port -eq 0) {
  $l = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, 0); $l.Start(); $Port = $l.LocalEndpoint.Port; $l.Stop()
}
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()
New-Item -ItemType Directory -Force (Join-Path $Root ".bwm") | Out-Null
@{port=$Port; pid=$PID} | ConvertTo-Json | Set-Content -Encoding utf8 $statePath
Write-Output "URL http://localhost:$Port/"
$types = @{ ".html"="text/html; charset=utf-8"; ".js"="text/javascript; charset=utf-8"; ".css"="text/css; charset=utf-8"; ".json"="application/json"; ".png"="image/png"; ".jpg"="image/jpeg"; ".svg"="image/svg+xml" }
while ($listener.IsListening) {
  $ctx = $listener.GetContext()
  $path = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath)
  if ($path -eq "/") { $path = "/index.html" }
  $file = Join-Path $Root ($path.TrimStart("/") -replace "/", "\")
  # Containment: resolve '..' before touching the disk, then require the result to sit under $Root.
  try { $full = [IO.Path]::GetFullPath($file) } catch { $full = $null }
  $inside = $full -and ($full -eq $Root -or $full.StartsWith($Root + [IO.Path]::DirectorySeparatorChar))
  if ($inside -and (Test-Path -LiteralPath $full -PathType Leaf)) {
    $bytes = [IO.File]::ReadAllBytes($full)
    $ext = [IO.Path]::GetExtension($full).ToLower()
    $ctx.Response.ContentType = if ($types.ContainsKey($ext)) { $types[$ext] } else { "application/octet-stream" }
    $ctx.Response.StatusCode = 200
  } else {
    $bytes = [Text.Encoding]::UTF8.GetBytes("not found: $path")
    $ctx.Response.ContentType = "text/plain; charset=utf-8"; $ctx.Response.StatusCode = 404
  }
  $ctx.Response.ContentLength64 = $bytes.Length
  $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  $ctx.Response.Close()
}
