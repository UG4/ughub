function __fish_ughub_packages
  ughub get-packagenames
end

function __fish_ughub_installed_packages
  ughub get-packagenames installed
end

set -l ughub_commands addsource help genprojectfiles git init install installall packageinfo list log repair updatesources version
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a addsource -d 'Adds a package-source (i.e. a git repository) from the given URL.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a help -d 'Gets help for a given command.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a genprojectfiles -d 'Generates project-files for the given TARGET platform.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a git -d 'Will run a git command on all installed packages.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a init -d 'Initializes a path for use with ughub. An .ughub folder is created.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a install -d 'Installs a ug package.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a installall -d 'Installs all ug packages.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a packageinfo -d 'Get information about a package.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a list -d 'Lists available packages.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a log -d 'Prints the git log of a package.'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a repair -d 'Attempts to repair a broken .ughub directory'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a updatesources -d 'Reloads the lists of available packages from the sources'
complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a version -d 'Prints version information'


complete -f -c ughub -n "__fish_seen_subcommand_from list" -a "-a --matchall -i --installed -n --notinstalled -s --source"
complete -f -c ughub -n "__fish_seen_subcommand_from help" -a "$ughub_commands"
complete -f -c ughub -n "__fish_seen_subcommand_from install" -a "(__fish_ughub_packages) -b --branch -d --dry -i --ignore --nodeps --noupdate -r --resolve -s --source"
complete -f -c ughub -n "__fish_seen_subcommand_from installall" -a "-b --branch -d --dry -i --ignore --nodeps --noupdate --notinstalled --installled -r --resolve -s --source"
complete -f -c ughub -n "__fish_seen_subcommand_from log" -a "(__fish_ughub_installed_packages) -n"
