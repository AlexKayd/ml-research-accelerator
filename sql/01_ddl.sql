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
    dataset_format VARCHAR(20),
    dataset_size_kb DECIMAL(12,2),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    download_url TEXT,
    repository_url TEXT,
    source_updated_at TIMESTAMP,
    search_vector TSVECTOR,
    
    UNIQUE(source, external_id),
    CONSTRAINT chk_status CHECK (status IN ('active', 'error', 'deleted'))
);

CREATE TABLE files (
    file_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_size_kb DECIMAL(12, 2),
    file_hash VARCHAR(255),
    is_data BOOLEAN DEFAULT TRUE,
    file_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (dataset_id, file_name),
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id) ON DELETE CASCADE
);

CREATE TABLE reports (
    report_id BIGSERIAL PRIMARY KEY,
    file_id BIGINT NOT NULL UNIQUE,
    bucket_name VARCHAR(255),
    object_key VARCHAR(512),
    input_file_hash VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    updated_at TIMESTAMP,
    processing_started_at TIMESTAMP,
    error_message TEXT,

    FOREIGN KEY (file_id) REFERENCES files(file_id),
    CONSTRAINT chk_report_status CHECK (status IN ('completed', 'failed', 'processing', 'deleting'))
);

CREATE TABLE favorite_datasets (
    user_id BIGINT NOT NULL,
    dataset_id BIGINT NOT NULL,

    PRIMARY KEY (user_id, dataset_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id) ON DELETE CASCADE
);

CREATE TABLE users_reports (
    user_id BIGINT NOT NULL,
    report_id BIGINT NOT NULL,

    PRIMARY KEY (user_id, report_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES reports(report_id) ON DELETE CASCADE
);


CREATE TRIGGER datasets_search_vector_update
    BEFORE INSERT OR UPDATE OF title, description ON datasets
    FOR EACH ROW
    EXECUTE FUNCTION tsvector_update_trigger(
        'search_vector', 'pg_catalog.english', 'title', 'description'
    );

UPDATE datasets SET search_vector = to_tsvector('pg_catalog.english', 
    COALESCE(title, '') || ' ' || COALESCE(description, ''));


CREATE INDEX idx_users_login ON users(login);

CREATE INDEX idx_datasets_search_vector ON datasets USING GIN(search_vector);
CREATE INDEX idx_datasets_source ON datasets(source);
CREATE INDEX idx_datasets_dataset_size_kb ON datasets(dataset_size_kb);
CREATE INDEX idx_datasets_dataset_format ON datasets(dataset_format);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_source_updated_at ON datasets(source_updated_at DESC);
CREATE INDEX idx_datasets_tags ON datasets USING GIN(tags);

CREATE INDEX idx_files_dataset_id ON files(dataset_id);
CREATE INDEX idx_reports_file_id ON reports(file_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_updated_at ON reports(updated_at DESC);
CREATE INDEX idx_reports_processing_started_at ON reports(processing_started_at DESC);

CREATE INDEX idx_favorites_user_id ON favorite_datasets(user_id);
CREATE INDEX idx_favorites_dataset_id ON favorite_datasets(dataset_id);

CREATE INDEX idx_users_reports_user_id ON users_reports(user_id);
CREATE INDEX idx_users_reports_report_id ON users_reports(report_id);