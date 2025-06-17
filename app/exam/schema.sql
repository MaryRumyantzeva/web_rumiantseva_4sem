-- Удаление таблиц, если они существуют (для чистого развертывания)
DROP TABLE IF EXISTS volunteer_registrations;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- Создание таблицы ролей
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(25) NOT NULL,
    description TEXT
) ENGINE=INNODB;

-- Создание таблицы пользователей
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(25) UNIQUE NOT NULL,
    first_name VARCHAR(25) NOT NULL,
    last_name VARCHAR(25) NOT NULL,
    middle_name VARCHAR(25) DEFAULT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=INNODB;

-- Создание таблицы мероприятий
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    location VARCHAR(128) NOT NULL,
    volunteers_needed INTEGER NOT NULL,
    image_filename VARCHAR(128) NOT NULL,
    organizer_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES users(id)
) ENGINE=INNODB;

-- Создание таблицы регистраций волонтеров (связь многие-ко-многим)
CREATE TABLE volunteer_registrations (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    event_id INTEGER NOT NULL,
    volunteer_id INTEGER NOT NULL,
    contact_info VARCHAR(128) NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(32) DEFAULT 'pending',
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (volunteer_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_status CHECK (status IN ('pending', 'accepted', 'rejected'))
) ENGINE=INNODB;

-- Вставка предопределенных ролей
INSERT INTO roles (name, description) VALUES 
('admin', 'Администратор (полный доступ к системе)'),
('moderator', 'Модератор (редактирование мероприятий и регистраций)'),
('user', 'Пользователь (просмотр и регистрация на мероприятия)');

-- Вставка тестового администратора (пароль: admin123)
INSERT INTO users (username, first_name, last_name, password_hash, role_id) 
VALUES ('admin', 'Иван', 'Иванов', SHA2('admin123', 256), 1);

-- Вставка тестового мероприятия
INSERT INTO events (title, description, date, location, volunteers_needed, image_filename, organizer_id)
VALUES (
    'Помощь бездомным животным',
    'Сбор волонтеров для помощи приюту бездомных животных',
    '2023-12-15',
    'ул. Пушкина, 10',
    15,
    'animals_help.jpg',
    1
);