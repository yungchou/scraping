import csv

with open('msdnforums.csv',errors='ignore') as input, open('msdn.forums.csv', 'w', newline='') as output:
    non_blank = (line for line in input if line.strip())
    output.writelines(non_blank)