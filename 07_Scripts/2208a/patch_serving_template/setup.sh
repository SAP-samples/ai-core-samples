#!/bin/bash


function _pre_requisite_cmd_check() {
    function isExecutable() {
        CNT=0
        FOUND=0
        for line in $(whereis $1); 
        do
            if [ $CNT -eq 0 ]; then
                CNT=$((CNT+1))
                continue
            elif [ $CNT -gt 0 ] && [[ -x $line ]]; then
                FOUND=1
            fi
            CNT=$((CNT+1))
        done
        if [ $FOUND -ne 1 ]; then
            log ERROR "${1} not found"
            show_help
            exit 1
        fi

    }

    # Verify kubectl is installed
    isExecutable python3


    isExecutable grep
}


function setup_requirement() {
    python3 -m venv ${TARGET_ENV}
    source ${TARGET_ENV}/bin/activate
    python3 -m pip install ruamel.yaml
}

function show_help() {
cat <<EOF

usage: $0 [python3 env location]

    This script will setup the python3 venv.
    If is not specify a directory will be create for you.

Usage steps after setup.

    1. source ${TARGET_ENV}/bin/activate

    2. python3 v1alpha2_to_v1beta1.py --help

EOF
}

function main() {
    local TARGET_ENV=
    if [ $# -eq 0 ]; then
        TARGET_ENV=$(date +%Y%m%d_%H%M)_env
    elif [ "$1" == "-h" ]; then
        show_help
        exit 0
    else
        TARGET_ENV=$1
    fi
    if [ ! -d ${TARGET_ENV} ]; then
        mkdir ${TARGET_ENV}
    fi
    echo "venv: ${TARGET_ENV}"

    _pre_requisite_cmd_check

    setup_requirement

    show_help
}

main $@
