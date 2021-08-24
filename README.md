# HospitalServer
Backend server logic for each hospital

ER Details

## Patient
- Patient ID (int primary sequential)
- Name
- DOB
- Gender
- ...
- Timestamp created
- Timestamp Updated
- isDeleted

# Activities (Django)

## Permission (Django)

## Employee
- Name
- Department(Oncology, Cardiac,...)
- type(Doctor, Nurse, Admin, ...)

## Visit
- Visit ID (int primary sequential)
- Public key of session passed by Patient
- Patient ID (foreign key)
- Timestamp created
- isDeleted

## Document types
- Document ID (int primary sequential)
- Document Name (Prescription, {CT Report, MRI, Blood report}, Diagnosis)

## Report
- Report ID ID (int primary sequential)
- Visit ID (foreign key)
- Document base64
- created Employee (foreign key)
- updated Employee (foreign key)
- Timestamp created
- Timestamp updated
- isDeleted
- Document Type


