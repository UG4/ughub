#compdef ughub

_ughub_completions() {
    local current_words="${words[CURRENT]}"
    local previous_words=("${words[@]:1:$CURRENT-1}")

    local suggestions=($(ughub getcompletions "${previous_words[@]}"))

    compadd -W "${suggestions[@]}" -- $current_word
}

compdef _ughub_completions ughub
