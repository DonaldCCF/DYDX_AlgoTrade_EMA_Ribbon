from datetime import datetime, timedelta
import pandas as pd
import math


# Format number
def format_number(curr_num, match_num):
    """
    Give current number an example of number with decimals desired
    Function will return the correctly formatted string
    """

    curr_num_string = f"{curr_num}"
    match_num_string = f"{match_num}"

    if "." in match_num_string:
        match_decimals = len(match_num_string.split(".")[1])
        curr_num_string = f"{curr_num:.{match_decimals}f}"
        curr_num_string = curr_num_string[:]
        return curr_num_string
    else:
        return f"{int(curr_num)}"


# Format time
def format_time(timestamp):
    return timestamp.replace(microsecond=0).isoformat()


# Get ISO Times
def get_ISO_times(entry_time, resolution):

    # Calculate candles needed
    now = convert_time(datetime.now())
    time_diff = now - entry_time
    print(time_diff)
    diff = math.ceil(time_diff.total_seconds() / (60*5))
    near_100 = int(math.ceil(diff / 100.0)) * 100
    total_call = near_100 / 100
    date_start = [now]

    # Get timestamps
    for i in range(0, int(total_call)):
        date_start.append(date_start[-1] - timedelta(minutes=100))

    # Format datetimes
    times_dict = {}

    for j in range(0, int(total_call)):
        new_key_values_dict = {"range_{}".format(j + 1): {"from_iso": format_time(date_start[j + 1]),
                                                          "to_iso": format_time(date_start[j])}}
        times_dict.update(new_key_values_dict)

    # Return result
    return times_dict


def convert_time(time):
    con_time = time.strftime("%Y-%m-%d %H:%M:%S")
    con_time = pd.to_datetime(con_time)
    return con_time
