param (
    [string]$src_7z,
    [string]$dest_path,
    [switch]$admin = $False
)

$dirPath = Split-Path -parent $MyInvocation.MyCommand.Definition
$cmdFile = Join-Path $dirPath "update.cmd"

if ($admin) {
    Start-Process -FilePath $env:ComSpec -ArgumentList '/c', "call", """$cmdFile""", """$src_7z""", """$dest_path""" -Verb RunAs -Wait
}
else {
    Start-Process -FilePath $env:ComSpec -ArgumentList '/c', "call", """$cmdFile""", """$src_7z""", """$dest_path""" -Wait
}

$kp_exe = Join-Path $dest_path "Keypirinha.exe"
Start-Process -FilePath $kp_exe
