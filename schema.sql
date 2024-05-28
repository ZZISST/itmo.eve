CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    creator_id BIGINT NOT NULL,
    photo_url TEXT,
    title VARCHAR(255) NOT NULL,
    tags VARCHAR(255),
    description TEXT,
    event_date TIMESTAMP NOT NULL,
    location VARCHAR(255),
    useful_links TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE participants (
    participant_id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(event_id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_event_id ON events(event_id);
CREATE INDEX idx_user_id ON participants(user_id);