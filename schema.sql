DROP TABLE IF EXISTS content_contributor;
DROP TABLE IF EXISTS visual_content;
DROP TABLE IF EXISTS written_content;
DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS contributor;
DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS section;

CREATE TABLE issue (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    `name` TEXT
) ENGINE=INNODB;

CREATE TABLE section (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    `name` TEXT
) ENGINE=INNODB;

CREATE TABLE content (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `title` TEXT,
    `subtitle` TEXT,
    `description` TEXT,
    `expanded_description` TEXT,
    `content` MEDIUMTEXT,
    `issue_id` INT,
    `section_id` INT,
    `misc_data` TEXT,
    `type` TEXT,
    FOREIGN KEY (`issue_id`)
        REFERENCES issue(`id`)
        ON DELETE CASCADE,
    FOREIGN KEY (`section_id`)
        REFERENCES section(`id`)
        ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE written_content (
    `content_id` INT NOT NULL PRIMARY KEY,
    FOREIGN KEY (`content_id`)
        REFERENCES content(`id`)
        ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE visual_content (
    `content_id` INT NOT NULL PRIMARY KEY,
    `file_path` TEXT,
    FOREIGN KEY (`content_id`)
        REFERENCES content(`id`)
        ON DELETE CASCADE
) ENGINE=INNODB;


CREATE TABLE contributor (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` TEXT
) ENGINE=INNODB;


CREATE TABLE content_contributor (
    `content_id` INT NOT NULL,
    `contributor_id` INT NOT NULL,

    FOREIGN KEY (`content_id`)
        REFERENCES content(`id`)
        ON DELETE CASCADE,

    FOREIGN KEY (`contributor_id`)
        REFERENCES contributor(`id`)
        ON DELETE CASCADE,

    UNIQUE INDEX(`content_id`, `contributor_id`)
) ENGINE=INNODB;
