$scriptblock = {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $tokens = $commandAst.Extent.Text.Trim() -split ' '
    $first, $rest = $tokens
    $completions = &"ughub" get-completions $rest

    $completions | Where-Object {$_ -like "${wordToComplete}*"} | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}

Register-ArgumentCompleter -Native -CommandName ughub -ScriptBlock $scriptblock