import csv
import sys

input_file = "sales-data.csv"
output_file = "sales-below-average.csv"

def average_price_per_foot(filename):
    total_price = 0
    total_sqft = 0
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                price = float(row['price'])
                sqft = float(row['sq__ft'])
            except ValueError:
                # Skip rows with invalid data
                continue
            total_price += price
            total_sqft += sqft

    if total_sqft == 0:
        print("Error: Total square footage is zero, cannot compute average.")
        sys.exit(1)

    avg_price_per_sqft = total_price / total_sqft
    return avg_price_per_sqft

def filter_below_avg(input_file, output_file):
    avg = average_price_per_foot(input_file)
    print(f"Average price per square foot across all properties: {avg:.2f}")

    with open(input_file, newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                price = float(row['price'])
                sqft = float(row['sq__ft'])
                if sqft == 0:
                    continue
            except ValueError:
                continue

            price_per_sqft = price / sqft
            if price_per_sqft < avg:
                writer.writerow(row)

    print(f"Filtered data written to {output_file}")

if __name__ == "__main__":
    filter_below_avg(input_file, output_file)

