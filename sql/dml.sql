INSERT INTO users (login, hashed_password, created_at) VALUES
    ('alexandra', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cJ36p.2mi', DEFAULT),
    ('testuser',  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cJ36p.2mi', DEFAULT),
    ('ivan',      '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cJ36p.2mi', DEFAULT),
    ('maria',     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2cJ36p.2mi', DEFAULT);


INSERT INTO datasets (source, external_id, title, description, tags, file_format, file_size_mb, download_url, repository_url) VALUES
    ('kaggle', 'uciml/iris', 'Iris Dataset', 'Классический набор данных для классификации цветов ириса', ARRAY['classification', 'biology', 'beginner'], 'CSV', 0.5, 'https://storage.googleapis.com/example/iris.csv', 'https://kaggle.com/datasets/uciml/iris'),
    ('kaggle', 'titanic', 'Titanic: Machine Learning from Disaster', 'Предсказание выживаемости на Титанике', ARRAY['classification', 'binary', 'beginner'], 'CSV', 1.2, 'https://storage.googleapis.com/example/titanic.csv', 'https://kaggle.com/c/titanic'),
    ('uci', 'wine', 'Wine Dataset', 'Данные о химическом составе вин', ARRAY['classification', 'chemistry'], 'CSV', 0.8, 'https://archive.ics.uci.edu/ml/machine-learning-databases/wine/wine.data', 'https://archive.ics.uci.edu/dataset/109/wine'),
    ('huggingface', 'datasets/iris', 'Iris (HuggingFace)', 'Набор данных ириса с Hugging Face', ARRAY['classification'], 'JSON', 0.6, 'https://huggingface.co/datasets/iris/resolve/main/data.json', 'https://huggingface.co/datasets/iris');

UPDATE datasets SET title = title WHERE title IS NOT NULL;

INSERT INTO reports (dataset_id, status, content) VALUES
    (1, 'completed', '{"total_rows":150,"total_columns":5,"missing_values":0,"correlations":{"sepal_length":0.78,"sepal_width":-0.42}}'),
    (2, 'completed', '{"total_rows":891,"total_columns":12,"missing_values":177,"correlations":{"survived":0.5,"age":-0.07}}'),
    (3, 'completed', '{"total_rows":178,"total_columns":13,"missing_values":0,"correlations":{"alcohol":0.8,"malic_acid":0.1}}'),
    (4, 'completed', '{"total_rows":150,"total_columns":5,"missing_values":0,"preview":"similar to iris"}');

INSERT INTO favorite_datasets (user_id, dataset_id) VALUES
    (1, 1),
    (1, 2),
    (2, 2),
    (2, 3),
    (3, 4),
    (4, 1);

INSERT INTO users_reports (user_id, report_id) VALUES
    (1, 1),
    (1, 2),
    (2, 2),
    (2, 3),
    (3, 4),
    (4, 1);