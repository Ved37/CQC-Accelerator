import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Number of records
N = 1000000

# Lists for random data generation
first_names = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Sophia', 'Jackson', 'Isabella', 'Lucas', 'Mia']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
conditions = ['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'Migraine', 'Allergy', 'None']
medications = ['Lisinopril', 'Metformin', 'Albuterol', 'Ibuprofen', 'Sumatriptan', 'Cetirizine', 'Amoxicillin']
specialties = ['Cardiology', 'Endocrinology', 'Pulmonology', 'Rheumatology', 'Neurology', 'General Practice']

# Generate Patients data
patients = pd.DataFrame({
    'patient_id': range(1, N + 1),
    'first_name': [random.choice(first_names) for _ in range(N)],
    'last_name': [random.choice(last_names) for _ in range(N)],
    'date_of_birth': [datetime(1950, 1, 1) + timedelta(days=random.randint(0, 25550)) for _ in range(N)],
    'primary_condition': [random.choice(conditions) for _ in range(N)]
})

# Generate Appointments data
appointments = pd.DataFrame({
    'appointment_id': range(1, N + 1),
    'patient_id': np.random.choice(patients['patient_id'], N),
    'appointment_date': [datetime(2023, 1, 1) + timedelta(days=random.randint(0, 730)) for _ in range(N)],
    'doctor_specialty': [random.choice(specialties) for _ in range(N)],
    'visit_reason': [random.choice(['Checkup', 'Follow-up', 'Emergency', 'Consultation']) for _ in range(N)]
})

# Generate Prescriptions data
prescriptions = pd.DataFrame({
    'prescription_id': range(1, N + 1),
    'appointment_id': np.random.choice(appointments['appointment_id'], N),
    'medication_name': [random.choice(medications) for _ in range(N)],
    'dosage': [f'{random.randint(5, 100)} mg' for _ in range(N)],
    'duration_days': np.random.randint(7, 90, N)
})

# Save to CSV files
patients.to_csv('data/patients.csv', index=False)
appointments.to_csv('data/appointments.csv', index=False)
prescriptions.to_csv('data/prescriptions.csv', index=False)

# Generate SQL join queries
join_queries = """
-- Query 1: Join Patients and Appointments to get patient visit history
SELECT 
    p.patient_id,
    p.first_name,
    p.last_name,
    a.appointment_id,
    a.appointment_date,
    a.doctor_specialty
FROM patients p
INNER JOIN appointments a ON p.patient_id = a.patient_id
LIMIT 10;

-- Query 2: Join all three tables to get complete patient treatment details
SELECT 
    p.patient_id,
    p.first_name,
    p.primary_condition,
    a.appointment_id,
    a.visit_reason,
    pr.prescription_id,
    pr.medication_name,
    pr.dosage
FROM patients p
INNER JOIN appointments a ON p.patient_id = a.patient_id
INNER JOIN prescriptions pr ON a.appointment_id = pr.appointment_id
LIMIT 10;

-- Query 3: Left join to find patients with or without appointments
SELECT 
    p.patient_id,
    p.first_name,
    p.last_name,
    COUNT(a.appointment_id) as appointment_count
FROM patients p
LEFT JOIN appointments a ON p.patient_id = a.patient_id
GROUP BY p.patient_id, p.first_name, p.last_name
LIMIT 10;

-- Query 4: Count prescriptions per patient condition
SELECT 
    p.primary_condition,
    COUNT(pr.prescription_id) as prescription_count
FROM patients p
INNER JOIN appointments a ON p.patient_id = a.patient_id
INNER JOIN prescriptions pr ON a.appointment_id = pr.appointment_id
GROUP BY p.primary_condition
ORDER BY prescription_count DESC
LIMIT 10;
"""

# Save SQL queries to a file
with open('healthcare_join_queries.sql', 'w') as f:
    f.write(join_queries)

print("CSV files (patients.csv, appointments.csv, prescriptions.csv) and SQL queries (healthcare_join_queries.sql) have been generated.")