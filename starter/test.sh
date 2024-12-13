#!/bin/bash

# Loop through all .bx files in the "examples" folder
for bx_file in examples/*.bx; do
    # Get the base name of the file (without extension)
    base_name=examples/$(basename "$bx_file" .bx)
    b=$(basename "$bx_file" .bx)
    #echo "Processing $bx_file..."

    # Run the first command
    python3 bxc.py "$bx_file"


    # Check if the required 'source.tac.json' file is created
    if [ ! -f "$base_name.tac.json" ]; then
        echo "Error: source.tac.json not created, skipping further processing for $bx_file."
        continue  # Skip the remaining commands and move to the next file
    fi

    # Run the remaining commands
    gcc -c bxlib/bx_runtime.c -o bxlib/bx_runtime.o

    gcc -o "$base_name.exe" "$base_name.x64-linux.s" bxlib/bx_runtime.o

    
    # Capture the output of the executable into a variable
    output=$(./"$base_name.exe")

    # Check if an expected output file exists
    if [ -f "expected/$b" ]; then
        # Compare the actual output to the expected output
        expected_output=$(cat "expected/$b")
        
        if [ "$output" == "$expected_output" ]; then
            echo "Success: Output for $bx_file is correct."
        else
            echo "Error: Output for $bx_file does not match the expected output."
            echo "Actual output:"
            echo "$output"
            echo "Expected output:"
            echo "$expected_output"
        fi
    else
        echo "Warning: No expected output file found for $bx_file."
    fi
    
    rm "$base_name.x64-linux.s"
    rm "$base_name.s"
    rm "$base_name.exe"
    rm "$base_name.tac.json"
    rm "$base_name.opt.tac.json"
    rm "bxlib/bx_runtime.o"

    #echo "$bx_file processed."
done
