#!/bin/bash


# Loop through all .bx files in the "examples" folder
for bx_file in regression/*.bx; do
    # Get the base name of the file (without extension)
    base_name=$(basename "$bx_file" .bx)

    echo "Processing $bx_file..."

    # Run the commands for each file
    python3 bxc.py "$bx_file"

    if [ ! -f "$base_name.tac.json" ]; then
        # echo "Error: $base_name.tac.json not created, skipping further processing for $bx_file."
        continue  # Skip the remaining commands and move to the next file
    fi


    python3 tac2x64.py "source.tac.json"
    gcc -o "source.exe" "source.s"
    ./"source.exe"
    rm "source.exe"
    rm "source.s"
    rm "source.tac.json"
    #echo "$bx_file processed."
done