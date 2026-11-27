#!/usr/bin/env bash

# Check if oscap is installed
if ! command -v oscap &> /dev/null; then
    echo "ERROR: oscap is not installed. Please install the openscap-scanner package." >&2
    exit 1
fi

# Use available CPUs, but avoid launching too many memory-intensive scanners.
default_jobs=$(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
if [[ ! $default_jobs =~ ^[1-9][0-9]*$ ]]; then
    default_jobs=1
fi
if [ "$default_jobs" -gt 4 ]; then
    default_jobs=4
fi
OSCAP_JOBS=${OSCAP_JOBS:-$default_jobs}
if [[ ! $OSCAP_JOBS =~ ^[1-9][0-9]*$ ]]; then
    echo "ERROR: OSCAP_JOBS must be a positive integer." >&2
    exit 1
fi

check_product_xml_files() (
    xml_files=()
    # Find all .xml files under products/*/
    while IFS= read -r -d '' xml_file; do
        xml_files+=("$xml_file")
    done < <(find products/*/ -name "*.xml" -type f -print0 2>/dev/null)

    if [ ${#xml_files[@]} -eq 0 ]; then
        return 0
    fi

    OSCAP_RESULTS_DIR=$(mktemp -d) || return 1
    export OSCAP_RESULTS_DIR
    trap 'rm -rf "$OSCAP_RESULTS_DIR"' EXIT

    # Each worker records failures separately so the parent can report them together.
    for index in "${!xml_files[@]}"; do
        printf '%s\0%s\0' "$index" "${xml_files[$index]}"
    done | xargs -0 -n 2 -P "$OSCAP_JOBS" bash -c '
        index=$1
        xml_file=$2
        echo "Checking: $xml_file"
        if output=$(oscap info "$xml_file" 2>&1); then
            exit 0
        fi
        printf "%s\n" "$output" > "$OSCAP_RESULTS_DIR/$index"
    ' _
    pipeline_status=("${PIPESTATUS[@]}")
    if [ "${pipeline_status[0]}" -ne 0 ] || [ "${pipeline_status[1]}" -ne 0 ]; then
        echo "ERROR: Parallel validation could not complete." >&2
        return 1
    fi

    failed_files=()
    for index in "${!xml_files[@]}"; do
        if [ -f "$OSCAP_RESULTS_DIR/$index" ]; then
            echo "ERROR: oscap info failed for ${xml_files[$index]}" >&2
            cat "$OSCAP_RESULTS_DIR/$index" >&2
            failed_files+=("${xml_files[$index]}")
        fi
    done

    if [ ${#failed_files[@]} -gt 0 ]; then
        echo "" >&2
        echo "Summary: ${#failed_files[@]} file(s) failed validation:" >&2
        printf '  %s\n' "${failed_files[@]}" >&2
        return 1
    fi

    return 0
)

check_product_xml_files
