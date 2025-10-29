CREATE TABLE Patient(
id SERIAL PRIMARY KEY,
first_name VARCHAR(50),
last_name VARCHAR(50),
patronymic VARCHAR(50),
passport_number VARCHAR(10),
insurance_number VARCHAR(20),
phone_number VARCHAR(20),
email VARCHAR(100),
gender VARCHAR(6),
birth_date DATE
);

CREATE TABLE Specialization(
id SERIAL PRIMARY KEY,
name VARCHAR(50)
);

CREATE TABLE Doctor(
id SERIAL PRIMARY KEY,
first_name VARCHAR(50),
last_name VARCHAR(50),
patronymic VARCHAR(50),
specialization_id INTEGER REFERENCES Specialization(id)
);

CREATE TABLE Service(
id SERIAL PRIMARY KEY,
specialization_id INTEGER REFERENCES Specialization(id),
service_name VARCHAR(100),
description VARCHAR(100),
price INTEGER,
duration_minutes INTEGER
);

CREATE TABLE Schedule(
id SERIAL PRIMARY KEY,
doctor_id INTEGER REFERENCES Doctor(id),
office_number VARCHAR(10),
service_id INTEGER REFERENCES Service(id),
date DATE,
start_time TIME,
end_time TIME,
is_available BOOL
);

CREATE TABLE Appointment(
id SERIAL PRIMARY KEY,
patient_id INTEGER REFERENCES Patient(id),
schedule_id INTEGER REFERENCES Schedule(id),
service_id INTEGER REFERENCES Service(id),
status VARCHAR(50),
information VARCHAR(500)
);

CREATE TABLE Contradiction(
medicament_name VARCHAR(50),
contradiction VARCHAR(50)
);

CREATE TABLE Patient_contradiction(
patient_id INTEGER REFERENCES Patient(id),
contradiction VARCHAR(50)
);
