diasub.substitute()
{
    local reslist devlist libdir includedir bindir cmd i perl_version \
    vendor_perl \
    cmdlist='sed shred perl dirname
    basename cat ls id cut bash man mktemp egrep date env mv sudo
    cp chmod ln chown rm printf touch head mkdir find file'

    declare -A Devlist=(
    [diasub]=diasub
    )
    cmdlist="${Devlist[@]} $cmdlist"
    for cmd in $cmdlist;do
        i=($(\builtin type -afp $cmd))
        [[ -z $i ]] && {
            [[ -z ${Devlist[$cmd]} ]] && reslist+=" $cmd" || devlist+=" $cmd"
        }
        \builtin eval "local ${cmd//-/_}=${i:-:}"
    done
    [[ -n $reslist ]] && {
        \builtin printf "%s\n" "$FUNCNAME Require: $reslist"
        return
    }
    [[ -n $devlist ]] && \builtin printf "%s\n" "$FUNCNAME Optional: $devlist"

    libdir=/usr/local/lib
    includedir=/usr/local/include/
    bindir=/usr/local/bin/

    \builtin source <($cat<<-SUB

diasub.reconfig()
{
    local help='[dictionary file][source srt file][target *.cn|en link file: will be created]'
    local dict=\${1:?\$help}
    local source=\${2:?\$help}
    local target=\${3:?\$help}
    $ln -fs ../\$dict misc/dictionary
    $ln -fs ../\$source misc/source
    $ln -fs ../\$target misc/target
}
diasub.pretranslate()
{
    diasub.py.install 1
    $diasub -o misc/source misc/dictionary
}
diasub.posttranslate()
{
    diasub.py.install 1
    $diasub -i misc/source misc/dictionary misc/target
}
diasub.py.install()
{
    [[ \${PWD##*/} =~ diasub ]] || return 
    local debugging=\${1:-0}
    [[ \$debugging =~ [[:digit:]] ]] || debugging=1
    $sed -e "s;DEBUGGING;\${debugging};" \
    src/diasub.py > $bindir/diasub
    $chmod u=rwx,go=rx $bindir/diasub
}
diasub.exlcude()
{
    $cat<<-DIASUBEXCLUDE > .git/info/exclude
misc/source
misc/target
misc/dictionary
DIASUBEXCLUDE
}
SUB
)
}
diasub.substitute
builtin unset -f diasub.substitute
