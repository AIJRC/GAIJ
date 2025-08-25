#!/bin/bash

start_time=$(date +%s)

# Check if at least the required arguments are provided
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <folder_with_md_files> <path_to_companies_details.csv> <output_folder> [num_processes]"
    exit 1
fi

# Assign arguments to variables
md_folder="$1"
companies_file="$2"
output_folder="$3"
num_processes="${4:-8}"  # Use 8 as default if not provided

# Create output folder if it doesn't exist
mkdir -p "$output_folder"

# Function to process a single file
process_file() {
    md_file="$1"
    companies_file="$2"
    output_folder="$3"
    base_name=$(basename "$md_file" .md)
    output_file="$output_folder/${base_name}.csv"
    
    awk -F',' -v file="$md_file" '
        NR==1 {print $0; next}
        {
            for (i=1; i<=NF; i++) {
                exists="False"
                while ((getline line < file) > 0) {
                    if (index(line, $i) != 0) {
                        exists="True"
                        break
                    }
                }
                close(file)
                printf "%s%s", exists, (i==NF ? "\n" : ",")
            }
        }
    ' "$companies_file" > "$output_file"
}

export -f process_file

# Use GNU Parallel to process files in parallel with specified number of processes
find "$md_folder" -name "*.md" | parallel -j "$num_processes" process_file {} "$companies_file" "$output_folder"

file_count=$(find "$output_folder" -name "*.csv" | wc -l)

echo "All files processed. Results are in $output_folder"
end_time=$(date +%s)
execution_time=$((end_time - start_time))

echo "Processing complete."
echo "Total files checked: $file_count"
echo "Total execution time: $execution_time seconds"
echo "Number of parallel processes used: $num_processes"
