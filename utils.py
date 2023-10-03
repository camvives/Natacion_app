"""Collection of utility functions for common tasks. 
This simplify common operations and improve code readability"""

def convert_timestamp(mm_values, ss_values, sss_values):
    """Returns a list with timestamps formatted in mm:ss:sss or '99:99:999' 
        if any value is empty."""

    zipped_times = zip(mm_values, ss_values, sss_values)
    formatted_times = []

    for minu, sec, sss in zipped_times:
        if '' in (minu, sec, sss):
            formatted_times.append('99:99:999')
        else:
            formatted_times.append(f'{int(minu):02}:{int(sec):02}:{int(sss):03}')

    return formatted_times
