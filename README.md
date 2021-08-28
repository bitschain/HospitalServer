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

## Sample Python Script to understand the encoding, decoding, storage and sharing of keys
```python
from umbral import PublicKey, SecretKey
import base64

alices_secret_key = SecretKey.random()
alices_public_key = alices_secret_key.public_key()

serialized_public_key = base64.b64encode(bytes(alices_public_key)).decode('utf-8')
# Now, serialized_public_key has type string. It is stored in the database, as well as used to
# transfer the keys over the network

# Upon receiving the serialized_public_key string over the network, or after reading it from
# the database, we can re-construct the Public Key object using the code below
new_public_key_bytes = base64.b64decode(serialized_pub_key.encode('utf-8'))
new_public_key = PublicKey._from_exact_bytes(data=new_public_key_bytes)
```


