CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE datasets (
    dataset_id BIGSERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    tags TEXT[],
    file_format VARCHAR(20),
    file_size_mb DECIMAL(10,2),
    download_url TEXT NOT NULL,
    repository_url TEXT,
    file_hash VARCHAR(64),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    search_vector TSVECTOR,
    
    UNIQUE(source, external_id)
);

CREATE TABLE reports (
    report_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'processing',
    content JSONB
);

CREATE TABLE favorite_datasets (
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    dataset_id BIGINT NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, dataset_id)
);

CREATE TABLE users_reports (
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    report_id BIGINT NOT NULL REFERENCES reports(report_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, report_id)
);


CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';


CREATE TRIGGER tsvector_update_trigger
    BEFORE INSERT OR UPDATE ON datasets
    FOR EACH ROW
    EXECUTE FUNCTION tsvector_update_trigger(
        search_vector, 'pg_catalog.english', title, description
    );

CREATE TRIGGER update_datasets_last_updated
    BEFORE UPDATE ON datasets
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated_column();

UPDATE datasets SET search_vector = to_tsvector('english', 
    COALESCE(title, '') || ' ' || COALESCE(description, ''));


CREATE INDEX idx_datasets_search_vector ON datasets USING GIN(search_vector);
CREATE INDEX idx_datasets_source ON datasets(source);
CREATE INDEX idx_datasets_file_size_mb ON datasets(file_size_mb);
CREATE INDEX idx_datasets_file_format ON datasets(file_format);
CREATE INDEX idx_datasets_last_updated ON datasets(last_updated DESC);
CREATE INDEX idx_datasets_tags ON datasets USING GIN(tags);

CREATE INDEX idx_reports_dataset_id ON reports(dataset_id);
CREATE INDEX idx_reports_status ON reports(status);

CREATE INDEX idx_favorites_user_id ON favorite_datasets(user_id);
CREATE INDEX idx_favorites_dataset_id ON favorite_datasets(dataset_id);

CREATE INDEX idx_users_reports_user_id ON users_reports(user_id);
CREATE INDEX idx_users_reports_report_id ON users_reports(report_id);