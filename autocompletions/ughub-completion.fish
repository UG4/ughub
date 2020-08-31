function __fish_ughub_packages
  ughub list --namesonly 
end

function __fish_ughub_installed_packages
  ughub list --namesonly --installed
end

set -l ughub_commands (ughub help --commands)
for c in {$ughub_commands}
  complete -f -c ughub -n "not __fish_seen_subcommand_from $ughub_commands" -a $c -d (ughub help $c --shortdescription)
  complete -f -c ughub -n "__fish_seen_subcommand_from $c" -a "(ughub get-completions $c)"
end
