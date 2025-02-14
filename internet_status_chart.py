import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='Generate a github-like activity chart displaying link down events.')
parser.add_argument('-i', '--input', type=str, default='', help='Input file, i.e. netcheck ')
args = parser.parse_args()

if args.input == '':
    print('Error: input file required')
    exit()

# Load input file
lines = []
with open(args.input) as file:
    for line in file:
        lines.append(line)

# Parse it
daily_downtime = []
prev_date = None
cur_duration = 0
for i in range(len(lines)):
    line = lines[i]
    if 'LINK DOWN' in line:
        if 'TOTAL DOWNTIME' in lines[i+2]:
            downtime_line = lines[i+2]
            cur_date_str = ' '.join(line[49:-1].split(' ')[0:4])
            # only process the date, time is not relevant
            cur_date = datetime.strptime(cur_date_str, '%a %d %b %Y') # Dow dd Mon YYYY
            if cur_date != prev_date:
                if prev_date != None:
                    daily_downtime.append([prev_date, cur_duration])
                    cur_duration = 0
                prev_date = cur_date
            duration_str = downtime_line[49:-1].replace(' seconds.', '')
            duration = int(duration_str.split(' minutes and ')[0]) * 60 + int(duration_str.split(' minutes and ')[1])
            cur_duration += duration

# Truncate list to last 365 days
now = datetime.now()
daily_downtime = [x for x in daily_downtime if (now-x[0]) < timedelta(days=365)]

# Remove first entries if needed in order to start on a Monday
dow_1st_entry = daily_downtime[0][0].weekday()
if dow_1st_entry != 0:
    start_date = daily_downtime[0][0] + timedelta(days=7 - dow_1st_entry)
daily_downtime = [x for x in daily_downtime if x[0] >= start_date]

# Define the thresholds
downtimes_sec = []
for x in daily_downtime:
    downtimes_sec.append(x[1])

downtimes_sec.sort()
n_thresholds = 4

thresholds = []
for _ in range(n_thresholds):
    thresholds.insert(0, downtimes_sec[-1])
    t = downtimes_sec[-1] // 8
    downtimes_sec = [x for x in downtimes_sec if x < t]
thresholds.insert(0,0)

# Generate list containing downtime in seconds for each day, including days without downtime
date = start_date
events = []
while date < now:
    if daily_downtime and daily_downtime[0][0] == date:
        events.append(daily_downtime[0][1])
        daily_downtime.pop(0)
    else:
        events.append(0)
    date = date + timedelta(days=1)

# Function returning the value corresponding to a daily downtime
def value(downtime):
    i = 0
    for t in thresholds:
        if downtime <= t: return i
        i += 1

# Print month names on the first line
prev_month = start_date.month
date = start_date
print('    ', end='')
while date < now:
    if date.month != prev_month:
        prev_month = date.month
        print(date.strftime("%b"), end=' ')
        date = date + timedelta(days=14)
    else:
        date = date + timedelta(days=7)
        print('  ', end='')
print()

# generate heat graph with colors
colors = [ '\033[38;5;244m', '\033[38;5;20m', '\033[38;5;34m', '\033[38;5;178m', '\033[38;5;196m']
color_off = '\033[0m'
square = '■'
for dow in range(7):
    i = dow
    if dow == 0:
        print('Mon ', end='')
    elif dow == 2:
        print('Wed ', end='')
    elif dow == 4:
        print('Fri ', end='')
    elif dow == 6:
        print('Sun ', end='')
    else:
        print('    ', end='')
    while i < len(events):
        print(f'{colors[value(events[i])]}{square}{color_off}', end=' ')
        i += 7
    print()

# Legend
print()

def approx_time(x):
    if x < 3600:
        return f'{x // 60} min'
    else:
        return f'{x // 3600} h'

for i in range(len(thresholds)):
    print(f'{colors[i]}{square}{color_off} {"" if thresholds[i]==0 else "<="}{approx_time(thresholds[i])}', end=' ')
print()
