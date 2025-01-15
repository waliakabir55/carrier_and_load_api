CREATE TABLE IF NOT EXISTS loads (
    reference_number VARCHAR PRIMARY KEY,
    origin VARCHAR NOT NULL,
    destination VARCHAR NOT NULL,
    equipment_type VARCHAR NOT NULL,
    rate FLOAT NOT NULL,
    commodity VARCHAR NOT NULL
);

INSERT INTO loads (reference_number, origin, destination, equipment_type, rate, commodity) VALUES
    ('REF09460', 'Denver CO', 'Detroit MI', 'Dry Van', 868, 'Automotive Parts'),
    ('REF04684', 'Dallas TX', 'Chicago IL', 'Dry Van or Flatbed', 570, 'Agricultural Products'),
    ('REF09690', 'Detroit MI', 'Nashville TN', 'Dry Van', 1495, 'Industrial Equipment');