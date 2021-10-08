CREATE DATABASE  IF NOT EXISTS `dashboard`;

CREATE USER 'ffuser'@'localhost' IDENTIFIED BY 'forward7%The7foundation';
GRANT ALL PRIVILEGES ON * . * TO 'ffuser'@'localhost';
