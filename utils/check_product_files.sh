#!/usr/bin/env bash

# Check if oscap is installed
if ! command -v oscap &> /dev/null; then
    echo "ERROR: oscap is not installed. Please install the openscap-scanner package."
    exit 1
fi

check_product_xml_files() {
    local exit_code=0
    local failed_files=()

    # Find all .xml files under products/*/
    while IFS= read -r -d '' xml_file; do
        echo "Checking: $xml_file"
        if ! output=$(oscap info "$xml_file" 2>&1); then
            echo "ERROR: oscap info failed for $xml_file"
            echo "$output"
            failed_files+=("$xml_file")
            exit_code=1
        fi
    done < <(find products/*/ -name "*.xml" -type f -print0 2>/dev/null)

    # Print summary if there were failures
    if [ ${#failed_files[@]} -gt 0 ]; then
        echo ""
        echo "Summary: ${#failed_files[@]} file(s) failed validation:"
        printf '  %s\n' "${failed_files[@]}"
    fi

    return $exit_code
}

check_product_xml_files
