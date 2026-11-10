USE urban_transit_intelligence;

-- =========================================================
-- METRO TABLES
-- =========================================================

CREATE TABLE IF NOT EXISTS metro_agency (
    agency_id VARCHAR(50),
    agency_name VARCHAR(255),
    agency_url VARCHAR(500),
    agency_timezone VARCHAR(100),
    agency_lang VARCHAR(20),
    agency_phone VARCHAR(50),
    agency_fare_url VARCHAR(500),
    agency_email VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS metro_calendar (
    service_id VARCHAR(50),
    monday TINYINT,
    tuesday TINYINT,
    wednesday TINYINT,
    thursday TINYINT,
    friday TINYINT,
    saturday TINYINT,
    sunday TINYINT,
    start_date VARCHAR(20),
    end_date VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS metro_routes (
    route_id VARCHAR(50),
    agency_id VARCHAR(50),
    route_short_name VARCHAR(100),
    route_long_name VARCHAR(255),
    route_desc TEXT,
    route_type INT,
    route_url VARCHAR(500),
    route_color VARCHAR(20),
    route_text_color VARCHAR(20),
    route_sort_order INT,
    continuous_pickup INT,
    continuous_drop_off INT
);

CREATE TABLE IF NOT EXISTS metro_stops (
    stop_id VARCHAR(50),
    stop_code VARCHAR(100),
    stop_name VARCHAR(255),
    stop_desc TEXT,
    stop_lat DECIMAL(10,7),
    stop_lon DECIMAL(10,7)
);

CREATE TABLE IF NOT EXISTS metro_trips (
    route_id VARCHAR(50),
    service_id VARCHAR(50),
    trip_id VARCHAR(100),
    trip_headsign VARCHAR(255),
    trip_short_name VARCHAR(100),
    direction_id INT,
    block_id VARCHAR(100),
    shape_id VARCHAR(100),
    wheelchair_accessible INT,
    bikes_allowed INT
);

CREATE TABLE IF NOT EXISTS metro_stop_times (
    trip_id VARCHAR(100),
    arrival_time VARCHAR(20),
    departure_time VARCHAR(20),
    stop_id VARCHAR(50),
    stop_sequence INT,
    stop_headsign VARCHAR(255),
    pickup_type INT,
    drop_off_type INT,
    shape_dist_traveled DECIMAL(12,3),
    timepoint INT,
    pickup_booking_rule_id VARCHAR(100),
    drop_off_booking_rule_id VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS metro_shapes (
    shape_id VARCHAR(100),
    shape_pt_lat DECIMAL(10,7),
    shape_pt_lon DECIMAL(10,7),
    shape_pt_sequence INT,
    shape_dist_traveled DECIMAL(12,3)
);


-- =========================================================
-- CHECK TABLES
-- =========================================================

SELECT 'METRO TABLES CREATED' AS status;

SHOW TABLES;