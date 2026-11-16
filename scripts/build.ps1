param([string[]]$Tasks = @('assembleDebug','testDebugUnitTest'), [switch]$Offline)
$ErrorActionPreference='Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $projectRoot
if (Test-Path -LiteralPath (Join-Path $projectRoot 'content\unit-question-bank.json')) {
    & python (Join-Path $projectRoot 'scripts\build_unit_questions.py') --check
    if ($LASTEXITCODE -ne 0) { throw '단원 문제의 독립 검토·원본·앱 자산 검사가 실패했습니다.' }
}
$debugKeyPathFile = Join-Path $projectRoot '.android\debug-keystore-path.txt'
if (-not $env:SQLNOTE_DEBUG_KEYSTORE -and (Test-Path -LiteralPath $debugKeyPathFile)) {
    $env:SQLNOTE_DEBUG_KEYSTORE = (Get-Content -LiteralPath $debugKeyPathFile -Raw).Trim()
}
if ($env:SQLNOTE_DEBUG_KEYSTORE -and -not (Test-Path -LiteralPath $env:SQLNOTE_DEBUG_KEYSTORE)) {
    throw '기존 개발 서명 키를 찾지 못했습니다. SQLNOTE_DEBUG_KEYSTORE 경로를 확인하세요.'
}
if (-not $env:JAVA_HOME) { $env:JAVA_HOME='C:\Program Files\Android\Android Studio\jbr' }
$env:GRADLE_USER_HOME=if($env:SQLNOTE_GRADLE_USER_HOME){$env:SQLNOTE_GRADLE_USER_HOME}else{Join-Path $projectRoot '.gradle-user'}
if($env:SQLNOTE_GRADLE_RO_CACHE){$env:GRADLE_RO_DEP_CACHE=$env:SQLNOTE_GRADLE_RO_CACHE}
elseif(Test-Path -LiteralPath 'D:\.gradle\caches\modules-2') { $env:GRADLE_RO_DEP_CACHE='D:\.gradle\caches' }
$sdkPath = if($env:ANDROID_HOME) { $env:ANDROID_HOME } elseif($env:ANDROID_SDK_ROOT) { $env:ANDROID_SDK_ROOT } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
if(-not (Test-Path -LiteralPath $sdkPath)) { throw "Android SDK 경로가 없습니다. ANDROID_HOME을 설정하세요: $sdkPath" }
$sdkProperty = 'sdk.dir=' + $sdkPath.Replace('\','/').Replace(':','\:')
$escaped = -join ($sdkProperty.ToCharArray() | ForEach-Object { if([int]$_ -gt 127) { '\u{0:x4}' -f [int]$_ } else { [string]$_ } })
[System.IO.File]::WriteAllText((Join-Path $projectRoot 'local.properties'),$escaped,[System.Text.Encoding]::ASCII)
$localGradle = 'D:\.gradle\wrapper\dists\gradle-8.13-bin\5xuhj0ry160q40clulazy9h7d\gradle-8.13\bin\gradle.bat'
$extra=@('--console=plain','--stacktrace')
if($Offline) { $extra+='--offline' }
if(Test-Path -LiteralPath $localGradle) { & $localGradle @Tasks @extra } else { & .\gradlew.bat @Tasks @extra }
exit $LASTEXITCODE
