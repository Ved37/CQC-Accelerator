
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
