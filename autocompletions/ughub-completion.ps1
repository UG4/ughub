$scriptblock = {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $tokens = $commandAst.Extent.Text.Trim() -split '\s+'
    $all_packages = &"ughub" get-packagenames
    $all_packages = $all_packages.split(' ')    
    $installed_packages = &"ughub" get-packagenames installed
    $installed_packages = $installed_packages.split(' ')
    switch ($token) {
        
        'log' { $completions = $installed_packages + "-n"; break;}
        'install' { $completions = $all_packages + "-b","--branch","-d","--dry","-i","--ignore","--nodeps","--noupdate","-r","--resolve","-s","--source"; break;}
        'help' { $completions = "addsource","help","genprojectfiles","git","init","install","installall","packageinfo","list","log","repair","updatesources","version"; break }
        default { $completions = "addsource","help","genprojectfiles","git","init","install","installall","packageinfo","list","log","repair","updatesources","version" }
    }

    $completions | Where-Object {$_ -like "${wordToComplete}*"} | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}
Register-ArgumentCompleter -Native -CommandName ughub -ScriptBlock $scriptblock