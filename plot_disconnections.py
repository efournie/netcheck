import argparse
from datetime import datetime
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Generate a plot showing the number of disconnections per day.')
parser.add_argument('-i', '--input', type=str, default='/var/log/connection.log', help='Input file, i.e. netcheck log file')
parser.add_argument('-o', '--output', type=str, default='', help='Output image file')
parser.add_argument('-f', '--filter', type=str, default='', help='String used to filter the log file, can for example be the year')
args = parser.parse_args()

if args.input == '':
    print('Error: input file required')
    exit()

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
down_evts_dict = {}
with open(args.input) as file:
    for line in file:
        if 'LINK DOWN' in line and args.filter in line:
            evt_date_time_str = line.replace('LINK DOWN:', '').strip()
            date_str = f'{evt_date_time_str.split(" ")[3]}-{months.index(evt_date_time_str.split(" ")[2]) + 1:02d}-{evt_date_time_str.split(" ")[1]}'
            if date_str not in down_evts_dict:
                down_evts_dict[date_str] = 1
            else:
                down_evts_dict[date_str] += 1

down_evts_dates = []
down_evts_numbers = []
for d in list(down_evts_dict.keys()):
    n = down_evts_dict[d]
    down_evts_dates.append(datetime.fromisoformat(d))
    down_evts_numbers.append(n)

plt.figure(figsize=(14, 4))
plt.bar(down_evts_dates, down_evts_numbers)
plt.savefig(args.output)
