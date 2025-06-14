from collections import Counter

input_file = "tds_full_course_content.txt"
output_file = "tds_cleaned.txt"

# Step 1: Count frequency of all lines
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

line_counts = Counter(line.strip() for line in lines if line.strip())

# Step 2: Remove lines that occur too frequently (i.e. likely sidebar)
THRESHOLD = 8  # Adjust this if needed
filtered_lines = [
    line for line in lines
    if line.strip() == "" or line_counts[line.strip()] <= THRESHOLD
]

# Step 3: Write to cleaned file
with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(filtered_lines)

print(f"Cleaned file saved to {output_file}")
