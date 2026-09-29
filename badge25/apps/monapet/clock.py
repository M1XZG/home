import time


def _weekday_sunday_zero(year, month, day):
    offsets = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    if month < 3:
        year -= 1
    return (
        year + year // 4 - year // 100 + year // 400
        + offsets[month - 1] + day
    ) % 7


def _last_sunday(year, month):
    return 31 - _weekday_sunday_zero(year, month, 31)


def uk_offset_hours(utc):
    year, month, day, hour = utc[0], utc[1], utc[2], utc[3]

    if 4 <= month <= 9:
        return 1
    if month == 3:
        change_day = _last_sunday(year, month)
        return 1 if day > change_day or (
            day == change_day and hour >= 1
        ) else 0
    if month == 10:
        change_day = _last_sunday(year, month)
        return 1 if day < change_day or (
            day == change_day and hour < 1
        ) else 0
    return 0


def current_time_text():
    utc = time.gmtime()
    if utc[0] < 2025:
        return None

    local = time.gmtime(time.time() + uk_offset_hours(utc) * 3600)
    return "{:02d}:{:02d}".format(local[3], local[4])
