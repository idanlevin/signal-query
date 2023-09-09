#!/bin/sh

export_signal() {
    echo "Starting Signal DB copy script"

    # Source and target directories
    src="/Users/$USER/Library/Application Support/Signal/sql/db.sqlite"
    dest_dir="./db_copy"

    # Create dest dir if doesn't exist
    mkdir -p "$dest_dir"

    # Get current date and time in the format YYYY-MM-DD_HH-MM-SS
    current_datetime=$(date +"%Y-%m-%d_%H-%M-%S")

    # Extract the filename without extension
    filename=$(basename -- "$src")
    extension="${filename##*.}"
    filename="${filename%.*}"

    # Construct the new destination path with the date-time appended
    destname="${filename}_$current_datetime.$extension"
    dest="$dest_dir/$destname"

    # Copy the file
    cp "$src" "$dest"

    echo "File copied to: $dest"

    # Create a symlink to the latest file
    echo "Creating a 'db-latest' symlink"
    pushd "$dest_dir"
    ln -sf "$destname" "db-latest.sqlite"
    popd

    echo "Done!"

}

export_signal