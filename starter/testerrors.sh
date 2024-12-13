#!/bin/bash


# Loop through all .bx files in the "examples" folder
for bx_file in regression/exceptions*.bx; do
    # Get the base name of the file (without extension)
    base_name=$(basename "$bx_file" .bx)

    echo "Processing $bx_file..."

    # Run the commands for each file
    python3 bxc.py "$bx_file"

    if [ $? -ne 0 ]; then
        echo "Error: bxc.py failed for $bx_file, skipping further processing."
        echo ""
        continue  # Skip to the next file
    fi
done