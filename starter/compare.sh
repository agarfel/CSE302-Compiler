#!/bin/bash

# Loop through all .bx files in the "examples" folder
for bx_file in examples/*.bx; do
    if [ "$bx_file" == "examples/arithops.bx" ]; then
        continue
    fi
    # Get the base name of the file (without extension)
    base_name=examples/$(basename "$bx_file" .bx)
    b=$(basename "$bx_file" .bx)

    #echo "Processing $bx_file..."

    # Run the first command
    python3 bxc.py "$bx_file"

    # Check if the required 'source.tac.json' file is created
    if [ ! -f "$base_name.tac.json" ]; then
        echo "Error: source.tac.json not created, skipping further processing for $bx_file."
        break  # Skip the remaining commands and move to the next file
    fi

    # Run the remaining commands
    gcc -o "$base_name.exe" "$base_name.x64-linux.s"
    if [ $? -ne 0 ]; then
        echo "Error: .exe not created, skipping further processing for $bx_file."
        rm "$base_name.tac.json"
        rm "$base_name.opt.tac.json"
        rm "$base_name.x64-linux.s"
        break
    fi
    # Capture the output of the executable into a variable
    output=$(./"$base_name.exe")
    # Check if an expected output file exists
    
    rm "$base_name.tac.json"
    rm "$base_name.opt.tac.json"
    rm "$base_name.x64-linux.s"
    rm "$base_name.exe"

    # Compare the actual output to the expected output
    python3 ../solution/bxc.py "$bx_file"

    # Run the remaining commands
    gcc -o "$base_name.exe" "$base_name.s"
    if [ $? -ne 0 ]; then
        echo "Error: .exe not created, skipping further processing for $bx_file."
        rm "$base_name.tac.json"
        break
    fi
    # Capture the output of the executable into a variable
    expected_output=$(./"$base_name.exe")
    
    if [ "$output" != "$expected_output" ]; then
        echo "Error: Output for $bx_file does not match the expected output."
        echo "Actual output:"
        echo "$output"
        echo "Expected output:"
        echo "$expected_output"
        rm "$base_name.o"
        rm "$base_name.s"
        rm "$base_name.exe"
        continue
    fi

    rm "$base_name.o"
    rm "$base_name.s"
    rm "$base_name.exe"

#echo "$bx_file processed."
done
