#/usr/bin/env bash
_ughub_completions()
{
    local suggestions=$(ughub getcompletions ${COMP_WORDS[@]:1})
    COMPREPLY=($(compgen -W "${suggestions[@]}" -- "${COMP_WORDS[-1]}"))
}

complete -F _ughub_completions ughub
