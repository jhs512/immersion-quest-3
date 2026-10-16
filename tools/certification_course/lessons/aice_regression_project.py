"""aice-regression-project: one regression analysis from two raw files to a saved answer (AICE Associate 21st lesson).

Every task starts from the same two original files of a made-up bike rental service:
data/rentals.csv (rental_id, station_id, hour, temp, rain, distance, fee, minutes) and
data/stations.json (records of station_id and area). Like the older official regression sample,
the analysis begins by merging the two files on a key. Each starter already holds every earlier
pipeline step (read and merge, fix the temperature column, fill blanks and trim outliers, choose
X and y, one-hot and split, scale), so the tasks never share a run. The learner completes one step.

The rental logs come from random.Random(seed), so the bytes are fixed when the lesson is built:
- Some rentals use a new station missing from the JSON (left merge keeps them, area is blank),
  and the JSON lists a closed station with no rentals (right or outer merge adds a row).
- A few temperatures read '점검' (sensor check), so temp is read as text until to_numeric.
- A few rentals were returned very late, far above the IQR upper bound of minutes.
- fee is computed from minutes after the return, so it correlates with minutes almost perfectly:
  the leak column the correlation step points at.
Base 150 rows; the changed files have 128 and 176 rows with other stations, effects and counts,
so memorized shapes, row counts and scores fail. Trees stay small and the network stops early,
so one grade finishes well within 60 seconds.
"""
import json
import random

from certification_course.kit import py_task
from certification_course.kit_plots import plot_task
from certification_course.kit_tf import tf_task
from principles_course.common import code, lesson

SOURCES = ['https://aice.study/info/aice/asso',
           'https://aice.study/certi/practice',
           'https://pandas.pydata.org/docs/reference/api/pandas.merge.html',
           'https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html',
           'https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping',
           'https://xgboost.readthedocs.io/en/stable/python/python_api.html#module-xgboost.sklearn']

RENTALS = 'data/rentals.csv'
STATIONS = 'data/stations.json'


def _files(seed, rows, stations, *, closed, new, minutes_of, new_rows, checks, late):
    """One rental log and its station list.

    stations: {station_id: area}. closed is listed in the JSON but has no rentals; new has rentals
    but is missing from the JSON. minutes_of(distance, area, rain, temp) is the typical ride length.
    """
    rng = random.Random(seed)
    open_ids = [s for s in stations if s != closed]
    new_at = set(rng.sample(range(rows), new_rows))
    check_at = set(rng.sample(range(rows), checks))
    late_at = set(rng.sample(range(rows), late))
    lines = ['rental_id,station_id,hour,temp,rain,distance,fee,minutes']
    first = rng.randint(30, 90) * 100
    for i in range(rows):
        station = new if i in new_at else rng.choice(open_ids)
        hour = rng.randint(6, 22)
        temp = round(rng.uniform(3, 31), 1)
        rain = int(rng.random() < 0.25)
        distance = round(rng.uniform(0.5, 7.5), 1)
        minutes = minutes_of(distance, stations.get(station, '?'), rain, temp) + rng.uniform(-4, 4)
        if i in late_at:
            # Forgotten returns: hours instead of minutes.
            minutes += rng.randint(110, 220)
        minutes = max(3, round(minutes))
        # The fee is settled at return from the minutes; some members get 500 won off.
        fee = 1000 + 150 * minutes - (500 if rng.random() < 0.3 else 0)
        shown = '점검' if i in check_at else str(temp)
        lines.append(f'{first + i},{station},{hour},{shown},{rain},{distance},{fee},{minutes}')
    listed = [{'station_id': s, 'area': a} for s, a in stations.items()]
    return {RENTALS: '\n'.join(lines) + '\n', STATIONS: json.dumps(listed, ensure_ascii=False, indent=1) + '\n'}


BASE = _files(7, 150, {'S01': '강변', 'S02': '도심', 'S03': '공원', 'S04': '도심', 'S05': '강변', 'S06': '공원'},
              closed='S06', new='S07', new_rows=4, checks=4, late=3,
              minutes_of=lambda d, a, r, t: 5 + 4.2 * d + {'강변': 9, '공원': 5, '도심': 0}.get(a, 3) - 5 * r + 0.15 * (t - 15))
SHORT = _files(11, 128, {'B11': '공원', 'B12': '도심', 'B13': '강변', 'B14': '공원', 'B15': '도심'},
               closed='B14', new='B19', new_rows=3, checks=5, late=2,
               minutes_of=lambda d, a, r, t: 8 + 3.5 * d + {'강변': 6, '공원': 11, '도심': 1}.get(a, 4) - 3 * r + 0.3 * (t - 15))
LONG = _files(23, 176, {'K21': '도심', 'K22': '강변', 'K23': '도심', 'K24': '공원', 'K25': '강변', 'K26': '도심',
                        'K27': '공원'},
              closed='K23', new='K28', new_rows=6, checks=3, late=4,
              minutes_of=lambda d, a, r, t: 3 + 5 * d + {'강변': 12, '공원': 4, '도심': 0}.get(a, 2) - 6 * r + 0.1 * (t - 15))
SCENARIOS = [{'files': SHORT}, {'files': LONG}]
