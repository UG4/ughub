#/usr/bin/env bash
_ughub_completions()
{
    local suggestions=$(ughub get-completions ${COMP_WORDS[@]})
    COMPREPLY=($(compgen -W "${suggestions[@]}" "${COMP_WORDS[-1]}"))
}

complete -F _ughub_completions ughub
