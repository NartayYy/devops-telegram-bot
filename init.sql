USE bot_db;

CREATE TABLE IF NOT EXISTS user_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username VARCHAR(255),
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp)
);

CREATE TABLE IF NOT EXISTS bot_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    command VARCHAR(100) NOT NULL UNIQUE,
    count INT DEFAULT 1,
    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_command (command)
);

-- Вставляем начальные данные
INSERT INTO bot_stats (command, count) VALUES 
('start', 0),
('status', 0),
('stats', 0),
('docker', 0),
('k8s', 0) 
ON DUPLICATE KEY UPDATE count = count;
