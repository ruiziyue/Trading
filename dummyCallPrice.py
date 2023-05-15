#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  8 16:37:43 2023

@author: ericrui
"""

def process_columns(file_path, output_file_path):
    processed_columns = []
    with open(file_path, 'r') as file:
        for line in file:
            columns = line.strip().split(',')[:2]  # Extract first two columns
            columns += ['11.5'] * 4  # Add four additional columns with value 11.5
            processed_columns.append(columns)

    with open(output_file_path, 'w') as output_file:
        for columns in processed_columns:
            line = ','.join(columns) + '\n'  # Join columns with tab delimiter
            output_file.write(line)

# Example usage
input_file_path = 'ES2022-2023.txt'  # Replace with the path to your input text file
output_file_path = 'callprice.txt'  # Replace with the desired path for the output text file
process_columns(input_file_path, output_file_path)

filename = "callprice.txt"  # Replace with the actual file name

with open(filename, "r") as file:
    lines = file.readlines()  # Read all lines from the file

for i, line in enumerate(lines):
    if "0730" in line:
        columns = line.split(",")  # Split the line by comma
        columns[2:6] = ["5.75"] * 4  # Replace columns 3, 4, 5, and 6 with "5.75"
        lines[i] = ",".join(columns)+ '\n'  # Join the columns back into a line

with open('callprice_new.txt', "w") as file:
    file.writelines(lines)  # Write the modified lines back to the file