CREATE DATABASE IF NOT EXISTS hti_Automation;

CREATE USER IF NOT EXISTS 'g7admin'@'localhost' IDENTIFIED BY '1234g7';
GRANT ALL PRIVILEGES ON hti_Automation.* TO 'g7admin'@'localhost';
FLUSH PRIVILEGES;

USE hti_Automation;

CREATE TABLE IF NOT EXISTS device_status (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(50) UNIQUE NOT NULL,
    status      VARCHAR(50) NOT NULL
);

INSERT IGNORE INTO device_status (device_name, status) VALUES ('light',           'OFF');
INSERT IGNORE INTO device_status (device_name, status) VALUES ('security_system', 'OFF');
INSERT IGNORE INTO device_status (device_name, status) VALUES ('pir_1',           'SAFE');
INSERT IGNORE INTO device_status (device_name, status) VALUES ('gas_sensor',      'SAFE');
INSERT IGNORE INTO device_status (device_name, status) VALUES ('door_sensor',     'CLOSED');
