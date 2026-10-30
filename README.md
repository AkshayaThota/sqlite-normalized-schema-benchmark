# SQLite Normalized Schema Benchmark

A continuation of [sqlite-query-benchmark](https://github.com/AkshayaThota/sqlite-query-benchmark). That project ran queries on a single flat table. This one normalizes the same salary data into multiple related tables and measures how query performance changes with dataset size (1MB, 10MB, 100MB).

## Schema
- `persons`: PersonID, PersonName, BirthDate
- `schools`: SchoolID, SchoolName
- `campus`: SchoolID, SchoolCampus
- `department`: DepartmentID, DepartmentName
- `dept_campus`: links departments to school campuses
- `employment_records`: job, earnings, and foreign keys to the tables above

## What it does
- Loads each CSV and splits it into the normalized tables
- Runs the queries in `queries.txt` on each dataset
- Records execution times and writes results to a text file per database
- Plots time per query and time vs dataset size (log scale)

## Datasets
Only the 1MB dataset is included. The 10MB and 100MB files are too large for GitHub, so add them to the project folder to run the full benchmark.

## How to run
```
pip install -r requirements.txt
python main.py
```

## Tech used
Python, SQLite, pandas, matplotlib

## Results
Results_1.png
Results_2.png

## Author
Akshaya Thota