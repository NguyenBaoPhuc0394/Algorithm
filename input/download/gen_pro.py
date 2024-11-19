import random

with open('retail_utility.txt', 'r') as file:
    lines = file.readlines()

output_lines = []

for line in lines:
    probability = random.uniform(0.0001, 1) 

    probability = round(probability, 2)
    
    new_line = line.strip() + f":{probability}\n"
    
    output_lines.append(new_line)

# Ghi lại các dòng mới vào file output
with open('retail_utility_probability.txt', 'w') as file:
    file.writelines(output_lines)

print("xac suat da them")
