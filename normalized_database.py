import sqlite3
import pandas as pd
import time
import matplotlib.pyplot as plt 

def create_schema(conn):
    """Create normalized schema"""
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS persons (
        PersonID INTEGER PRIMARY KEY,
        PersonName TEXT,
        BirthDate TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schools (
        SchoolID INTEGER PRIMARY KEY,
        SchoolName TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campus (
        SchoolID INTEGER,
        SchoolCampus TEXT,
        PRIMARY KEY (SchoolID, SchoolCampus),
        FOREIGN KEY (SchoolID) REFERENCES schools(SchoolID)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS department (
        DepartmentID INTEGER PRIMARY KEY,
        DepartmentName TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dept_campus (
        DepartmentID INTEGER,
        SchoolID INTEGER,
        SchoolCampus TEXT,
        FOREIGN KEY (DepartmentID) REFERENCES department(DepartmentID),
        FOREIGN KEY (SchoolID, SchoolCampus) REFERENCES campus(SchoolID, SchoolCampus)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employment_records (
        StillWorking INTEGER,
        PersonID INTEGER,
        JobID INTEGER,
        JobTitle TEXT,
        Earnings REAL,
        EarningsYear INTEGER,
        SchoolID INTEGER,
        SchoolCampus TEXT,
        DepartmentID INTEGER,
        FOREIGN KEY (PersonID) REFERENCES persons(PersonID),
        FOREIGN KEY (SchoolID, SchoolCampus) REFERENCES campus(SchoolID, SchoolCampus),
        FOREIGN KEY (DepartmentID) REFERENCES department(DepartmentID)
    )''')
    conn.commit()

def load_and_normalize_data(csv_file, db_name):
    """Load CSV data into staging table and normalize into schema"""
    conn = sqlite3.connect(db_name)
    create_schema(conn)
    
    # Load CSV into DataFrame
    df = pd.read_csv(csv_file)
    
    # Insert data into normalized tables
    df[['PersonID', 'PersonName', 'BirthDate']].drop_duplicates().to_sql('persons', conn, if_exists='replace', index=False)
    df[['SchoolID', 'SchoolName']].drop_duplicates().to_sql('schools', conn, if_exists='replace', index=False)
    df[['SchoolID', 'SchoolCampus']].drop_duplicates().to_sql('campus', conn, if_exists='replace', index=False)
    df[['DepartmentID', 'DepartmentName']].drop_duplicates().to_sql('department', conn, if_exists='replace', index=False)
    df[['DepartmentID', 'SchoolID', 'SchoolCampus']].drop_duplicates().to_sql('dept_campus', conn, if_exists='replace', index=False)
    
    employment_records = df[['StillWorking', 'PersonID', 'JobID', 'JobTitle', 'Earnings', 'EarningsYear', 'SchoolID', 'SchoolCampus', 'DepartmentID']]
    employment_records.to_sql('employment_records', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Data from {csv_file} has been normalized and stored in {db_name}.")

def execute_query_with_timeout(cursor, query, timeout=300):
    start_time = time.time()
    cursor.execute(query)
    results = cursor.fetchall()
    elapsed_time = time.time() - start_time
    return elapsed_time, len(results)

def queries_execution(db_name, query_text, timeout=300):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    query_times = []
    
    output_file = f"{db_name}_results.txt"
    with open(output_file, 'w') as f:
        with open(query_text, 'r') as file:
            queries = file.readlines()
        
        for query in queries:
            query = query.strip()
            if query:
                try:
                    elapsed_time, result_count = execute_query_with_timeout(cursor, query, timeout)
                    query_times.append((query, elapsed_time))
                    
                    f.write(f"Query: {query}\n")
                    f.write(f"Execution time: {elapsed_time:.4f} seconds\n")
                    f.write(f"Result count: {result_count}\n")
                    
                    cursor.execute(query)
                    results = cursor.fetchall()
                    f.write("Results:\n")
                    for row in results:  
                        f.write(f"{row}\n")
                    if result_count > 10:
                        f.write(f"... (and {result_count - 10} more rows)\n")
                    f.write("\n")  
                    
                    print(f"Query executed in {elapsed_time:.2f} seconds. Results: {result_count}")
                except Exception as e:
                    f.write(f"Error executing query: {query}\n{str(e)}\n\n")
                    print(f"Error executing query: {e}")
    
    connect.close()
    print(f"Query results written to {output_file}")
    return query_times
 
datasets = {
    "salary_tracker_1MB": "salary_tracker_1MB.csv",
    "salary_tracker_10MB": "salary_tracker_10MB.csv",
    "salary_tracker_100MB": "salary_tracker_100MB.csv"
}
query_text = "queries.txt"

query_times_all = {dataset: [] for dataset in datasets.keys()}

for dataset_name, csv_dataset_path in datasets.items():
    db_name = f"{dataset_name}.db"
    load_and_normalize_data(csv_dataset_path, db_name)
    print(f"\nExecuting queries for database '{db_name}':")
    query_times = queries_execution(db_name, query_text)
    
    for query, time_taken in query_times:
        query_times_all[dataset_name].append(time_taken)
        print(f"\nquery: {query} | time taken: {time_taken:.4f} seconds")

query_labels = [f"Query {i+1}" for i in range(len(query_times))]
x = range(len(query_labels))

plt.figure(figsize=(12, 6))

for dataset, times in query_times_all.items():
    plt.plot(x, times, marker='o', label=dataset)

plt.xticks(x, query_labels)
plt.xlabel('Queries')
plt.ylabel('Execution Time (seconds)')
plt.title('Query Execution Time Based on File Sizes')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

plt.figure(figsize=(14, 8))

size_map = {'salary_tracker_1MB': 1, 'salary_tracker_10MB': 10, 'salary_tracker_100MB': 100}
x = [size_map[dataset] for dataset in datasets.keys()]

# Define line styles and colors for better visibility
line_styles = ['-', '--', '-.', ':']
colors = ['b', 'g', 'r', 'c', 'm', 'y']

# Plot each query as a separate line
for i in range(len(query_times)):
    query_times_across_datasets = [query_times_all[dataset][i] for dataset in datasets.keys()]
    plt.plot(x, query_times_across_datasets, marker='o', linestyle=line_styles[i % len(line_styles)], color=colors[i % len(colors)], label=f'Query {i+1}')

plt.xscale('log')  
plt.xlabel('Dataset Size (MB)')
plt.ylabel('Execution Time (seconds)')
plt.title('Query Execution Time vs Dataset Size')
plt.legend(loc='upper left', framealpha=0.7)  
plt.grid(True)

plt.xticks(x, [f'{size}MB' for size in x])

plt.tight_layout()
plt.show()

