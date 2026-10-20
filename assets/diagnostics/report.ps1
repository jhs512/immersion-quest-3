param([string]$DraftPath)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$draft = Get-Content -LiteralPath $DraftPath -Raw -Encoding UTF8 | ConvertFrom-Json
$folder = Split-Path -LiteralPath $DraftPath
$screen = Join-Path $folder 'screen.png'
$result = Join-Path $folder 'response.json'
$outcome = Join-Path $folder 'outcome.json'
$script:issueUrl = $null
$script:lastOutcome = ''
$form = New-Object System.Windows.Forms.Form
$form.Text = if ($draft.kind -eq 'content') { 'MQ · 문제 신고' } else { 'MQ · 앱 오류 신고' }
$form.Width = 700; $form.Height = 740; $form.StartPosition = 'CenterScreen'; $form.TopMost = $true
$workingArea = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$form.Width = [Math]::Min(700, $workingArea.Width)
$form.Height = [Math]::Min(740, $workingArea.Height)
$form.MinimumSize = New-Object System.Drawing.Size([Math]::Min(600,$workingArea.Width), [Math]::Min(640,$workingArea.Height))
$form.AutoScroll = $true
$form.Font = New-Object System.Drawing.Font('Segoe UI', 10)
$layout = New-Object System.Windows.Forms.TableLayoutPanel
$layout.Dock = 'Fill'; $layout.Padding = New-Object System.Windows.Forms.Padding(18); $layout.ColumnCount = 1; $layout.RowCount = 7
foreach ($height in @(58, 46, 200, 28, 40, 40, 48)) { [void]$layout.RowStyles.Add((New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, $height))) }
$layout.RowStyles[4].SizeType = 'Percent'; $layout.RowStyles[4].Height = 100
$heading = New-Object System.Windows.Forms.Label
$heading.Dock='Fill'; $heading.Text = "보낼 저장소: $($draft.repository)`n수업: $($draft.location.lesson_title) · 단계: $($draft.location.task_title)"
$layout.Controls.Add($heading,0,0)
$notice=New-Object System.Windows.Forms.Label
$notice.Dock='Fill'; $notice.Text='진단 파일은 링크로 접근할 수 있는 GitHub Gist에 저장해요. 이슈에 설명·환경·파일 링크를 올려요. 화면과 추가 설명에 공개하면 안 되는 내용이 없는지 확인하세요.'
$layout.Controls.Add($notice,0,1)
$picture=New-Object System.Windows.Forms.PictureBox
$picture.Dock='Fill'; $picture.SizeMode='Zoom'; $picture.BorderStyle='FixedSingle'; $layout.Controls.Add($picture,0,2)
$include=New-Object System.Windows.Forms.CheckBox
$include.Text='화면 캡처 포함'; $include.Checked=[bool]$draft.include_screen; $include.Dock='Fill'; $layout.Controls.Add($include,0,3)
$notes=New-Object System.Windows.Forms.TextBox
$notes.Multiline=$true; $notes.AcceptsReturn=$true; $notes.ScrollBars='Vertical'; $notes.Dock='Fill'; $notes.MaxLength=4000; $notes.Text=$draft.description
$layout.Controls.Add($notes,0,4)
$label=New-Object System.Windows.Forms.Label
$label.Dock='Fill'; $label.Text='위 칸에 어떤 일이 있었는지 자유롭게 적어주세요. 상세 기록 한 시간과 오래 보관한 이동 이력을 함께 보내요.'; $layout.Controls.Add($label,0,5)
$buttons=New-Object System.Windows.Forms.FlowLayoutPanel
$buttons.FlowDirection='RightToLeft'; $buttons.Dock='Fill'
$send=New-Object System.Windows.Forms.Button
$send.Text='보내기'; $send.Width=110; $send.Height=36; $send.Enabled=$false
$send.Add_Click({
    if ($script:issueUrl) {
        $start=New-Object System.Diagnostics.ProcessStartInfo($script:issueUrl)
        $start.UseShellExecute=$true
        [System.Diagnostics.Process]::Start($start) | Out-Null
        return
    }
    $send.Enabled=$false; $notes.ReadOnly=$true; $include.Enabled=$false; $cancel.Text='닫기'
    $notice.Text='GitHub에 신고를 보내고 있어요. 이 창을 닫아도 진행 중인 전송 결과는 로컬에 보관해요.'
    @{attempt=[DateTime]::UtcNow.Ticks.ToString();description=$notes.Text;include_screen=($include.Checked -and (Test-Path -LiteralPath $screen))} | ConvertTo-Json | Set-Content -LiteralPath $result -Encoding UTF8
})
$cancel=New-Object System.Windows.Forms.Button
$cancel.Text='취소'; $cancel.Width=100; $cancel.Height=36; $cancel.DialogResult='Cancel'
$buttons.Controls.Add($send); $buttons.Controls.Add($cancel); $layout.Controls.Add($buttons,0,6)
$form.CancelButton=$cancel
$form.Controls.Add($layout)
$timer=New-Object System.Windows.Forms.Timer
$timer.Interval=200; $started=[DateTime]::UtcNow
$timer.Add_Tick({
    if (Test-Path -LiteralPath $screen) {
        try {
            $bytes=[System.IO.File]::ReadAllBytes($screen)
            $stream=New-Object System.IO.MemoryStream(,$bytes)
            $image=[System.Drawing.Image]::FromStream($stream)
            $picture.Image=New-Object System.Drawing.Bitmap($image)
            $image.Dispose(); $stream.Dispose(); $timer.Stop(); $send.Enabled=$true
        } catch { }
    } elseif (([DateTime]::UtcNow-$started).TotalSeconds -gt 4) {
        $include.Checked=$false; $include.Enabled=$false; $include.Text='캡처를 준비하지 못했어요. 기록과 설명은 보낼 수 있어요.'; $timer.Stop(); $send.Enabled=$true
    }
})
$statusTimer=New-Object System.Windows.Forms.Timer
$statusTimer.Interval=250
$statusTimer.Add_Tick({
    if (Test-Path -LiteralPath $outcome) {
        try {
            $status=Get-Content -LiteralPath $outcome -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($status.attempt -eq $script:lastOutcome) {return}
            $script:lastOutcome=$status.attempt
            $notice.Text=$status.message
            $send.Enabled=$true
            if ($status.ok) {
                $script:issueUrl=$status.url; $send.Text='이슈 열기';$cancel.Text='닫기'
            } else {
                $notes.ReadOnly=$false; $include.Enabled=(Test-Path -LiteralPath $screen); $send.Text='다시 보내기';$cancel.Text='취소'
            }
        } catch { }
    }
})
$form.Add_Shown({$form.Activate();$notes.Focus();$timer.Start();$statusTimer.Start()})
$answer=$form.ShowDialog()
$timer.Stop();$timer.Dispose();$statusTimer.Stop();$statusTimer.Dispose()
if ($picture.Image) {$picture.Image.Dispose()}
$form.Dispose()
if ($answer -eq [System.Windows.Forms.DialogResult]::OK) {exit 0} else {exit 2}
