#!/usr/bin/env bash
##============================================================================
# Run kubeval to lint k8s manifests
# Adapted for Streetshares by dgoade from:
# https://github.com/instrumenta/kubeval/blob/master/docs/contrib.md
#
# Despite what the docs say, I was not able to get kubeval to output the
# name of the file that it checks with the "--filename" option, even when
# cating and piping the file through stdin like it says to do. e.g.
#   my-invalid-rc.yaml | kubeval --filename="my-invalid-rc.yaml"
# So I wrote this script to loop through the files that the pre-commit
# framework passes to kubeval and output the file name followed by kubeval's
# output.
##============================================================================

##---------------------------------
## Function definitions begin here
##---------------------------------

function validate_k8s_files {

  declare -i result=0

  for file in "${@}"; do
    >&2 echo "kubeval is checking ${file}..."
    kubeval -o stdout "${file}"
    (( result += ${?} ))
    echo "..................................................................."
  done

  return ${result}

}

##---------------------------------
## Main execution block
##---------------------------------

>&2 echo "Running kubeval validations..."
EXIT_STATUS=0
if ! [[ -x "$(command -v kubeval)" ]]; then
  >&2 echo 'Error: kubeval is not installed.' >&2
  EXIT_STATUS=1
fi

if (( "${EXIT_STATUS}" == 0 )); then
  validate_k8s_files "${@}"
  EXIT_STATUS=${?}
  if (( "${EXIT_STATUS}" > 0 )); then
    >&2 echo "Static analysis found violations that need to be fixed."
  fi
fi
exit ${EXIT_STATUS}
