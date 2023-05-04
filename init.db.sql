CREATE TABLE IF NOT EXISTS entertainment (
    item_id VARCHAR(200) PRIMARY KEY,
    title VARCHAR(2000),
    release_date VARCHAR(20),
    popularity NUMERIC(10,2),
    adult BOOLEAN,
    overview TEXT,
    trailer VARCHAR(2000),
    casts TEXT, 
    genre VARCHAR(2000),
    data_type VARCHAR(20) NOT NULL, 
    date_entry VARCHAR(20) NOT NULL
);
CREATE TABLE IF NOT EXISTS employees (
    email VARCHAR(200) PRIMARY KEY,
    name_person VARCHAR(200) NOT NULL,
    password_store VARCHAR(200) NOT NULL
);