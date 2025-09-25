Create Table Users (
	id INT PRIMARY KEY auto_increment,
    name VARCHAR(30) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'member', 'guest') DEFAULT "member"
);

CREATE Table Projects (
	id INT PRIMARY KEY auto_increment,
    name VARCHAR(30) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status ENUM("actif", "archivé") default "actif",
    owner_id INT,
    foreign key (owner_id) REFERENCES Users(id),
    created_at DATETIME DEFAULT current_timestamp
);

CREATE TABLE Tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    due_date DATE,
    status ENUM("todo", "en cours", "terminé") DEFAULT "todo",
    priority ENUM("basse", "moyenne", "haute", "critique") DEFAULT "moyenne",
    project_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    INDEX (status),
    INDEX (priority)
);

CREATE TABLE AssignedTasks (
    task_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (task_id, user_id),
    FOREIGN KEY (task_id) REFERENCES Tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE ProjectUsers (
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('owner', 'editor', 'viewer') DEFAULT 'viewer',
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES Projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);