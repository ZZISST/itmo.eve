CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    event_date TIMESTAMP NOT NULL,
    location TEXT NOT NULL,
    useful_links TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE participants (
    participant_id SERIAL PRIMARY KEY,
    event_id INT NOT NULL,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);