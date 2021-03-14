CREATE TABLE institutions(
	id INT UNSIGNED AUTO_INCREMENT,
	type VARCHAR(30) NOT NULL,
	name VARCHAR(50) NOT NULL,
	phone_number VARCHAR(20) NULL,
	address_id INT NOT NULL,
	PRIMARY KEY(id),
	FOREIGN KEY (address_id) REFERENCES addresses(id)
);

CREATE TABLE addresses(
	id INT UNSIGNED AUTO_INCREMENT,
	address VARCHAR(120),
	city VARCHAR(100),
	province VARCHAR(3),
	country VARCHAR(3),
	postal_code VARCHAR(16),
	PRIMARY KEY (id)
);

CREATE TABLE ratings(
	id INT UNSIGNED AUTO_INCREMENT,
	institution_id INT UNSIGNED,
	initiative_id INT UNSIGNED,
	rating INT,
	review VARCHAR(8000),
	PRIMARY KEY (id),
	FOREIGN KEY (institution_id) REFERENCES institutions(id),
	FOREIGN KEY (initiative_id) REFERENCES initiatives(id)
);

CREATE TABLES initiatives(
	id INT AUTO_INCREMENT,
	name VARCHAR(50) NOT NULL,
	institution_id INT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (institution_id) REFERENCES institutions(id)
);