#!/bin/bash

# Description: Script to determine changed modules between the current branch and the main branch
# Usage: ./determine_changed_modules.sh

# Validate that the script is being run inside a Git repository
if [ ! -d ".git" ]; then
  echo "Error: This script must be run inside a Git repository."
  exit 1
fi

# Fetch the origin/main branch
echo "Fetching origin/main..."
git fetch origin main

# Determine the current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Determine the comparison reference
if [ "$current_branch" == "main" ]; then
    # Find the parent of the current commit if on the main branch
    parent_commit=$(git log --pretty=format:"%H" -n 2 | tail -n 1)
    comparison="$parent_commit"
else
    # Compare with origin/main if on a different branch
    comparison="origin/main"
fi


# Get the list of modified directories containing a Makefile in the current branch with respect to the comparison commit
modified_dirs=$(git diff --name-only --relative "$comparison" | while read file; do
    dir=$(dirname "$file")
    if [[ "$dir" == models/* ]] && [ -e "$dir/Makefile" ]; then
        echo "$dir"
    fi
done)



# Filter out duplicates
modified_dirs_a=$(echo "$modified_dirs" | sort -u)

# Print the modified directories
echo "$modified_dirs_a"
