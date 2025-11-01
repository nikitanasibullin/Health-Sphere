-- Таблица пациент
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

-- Ограничения полей таблицы пациент

ALTER TABLE Patient
ADD CONSTRAINT check_name_format CHECK (first_name ~ '^[А-Я][а-я]+');
ALTER TABLE Patient
ALTER COLUMN first_name SET NOT NULL;

ALTER TABLE Patient
ADD CONSTRAINT check_lastname_format CHECK (last_name ~ '^[А-Я][а-я]+');
ALTER TABLE Patient
ALTER COLUMN last_name SET NOT NULL;

ALTER TABLE Patient
ADD CONSTRAINT check_patronymic_format CHECK (patronymic ~ '^[А-Я][а-я]+');

ALTER TABLE Patient
ALTER COLUMN passport_number SET NOT NULL;
ALTER TABLE Patient
ADD CONSTRAINT passport_number_unique UNIQUE (passport_number);

ALTER TABLE Patient
ALTER COLUMN insurance_number SET NOT NULL;
ALTER TABLE Patient
ADD CONSTRAINT insurance_number_unique UNIQUE (insurance_number);

ALTER TABLE Patient
ALTER COLUMN phone_number SET NOT NULL;
ALTER TABLE Patient
ADD CONSTRAINT phone_number_unique UNIQUE (phone_number);
ALTER TABLE Patient
ADD CONSTRAINT phone_number_check CHECK (phone_number ~ '^[0-9]+$');

ALTER TABLE Patient
ALTER COLUMN email SET NOT NULL;
ALTER TABLE Patient
ADD CONSTRAINT email_unique UNIQUE (email);
ALTER TABLE Patient
ADD CONSTRAINT email_format_check CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]+$');

ALTER TABLE Patient
ALTER COLUMN gender SET NOT NULL;
ALTER TABLE Patient
ADD CONSTRAINT gender_check CHECK (gender IN ('муж','жен'));

ALTER TABLE Patient
ALTER COLUMN birth_date SET NOT NULL;


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
information TEXT
);

CREATE TABLE Contradiction(
medicament_name VARCHAR(50),
contradiction VARCHAR(50)
);

CREATE TABLE Patient_contradiction(
patient_id INTEGER REFERENCES Patient(id),
contradiction VARCHAR(50)
);
