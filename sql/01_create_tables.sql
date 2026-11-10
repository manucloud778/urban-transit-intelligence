-- ============================================
-- URBAN TRANSIT INTELLIGENCE
-- DELHI BUS GTFS - MYSQL DATABASE
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS urban_transit_intelligence;

USE urban_transit_intelligence;


-- ============================================
-- 1. AGENCY
-- ============================================

CREATE TABLE IF NOT EXISTS agency (
    agency_id VARCHAR(50) PRIMARY KEY,
    agency_name VARCHAR(255),
    agency_url VARCHAR(500),
    agency_timezone VARCHAR(100),
    agency_lang VARCHAR(20),
    agency_phone VARCHAR(50),
    agency_fare_url VARCHAR(500)
);


-- ============================================
-- 2. ROUTES
-- ============================================

CREATE TABLE IF NOT EXISTS routes (
    agency_id VARCHAR(50),
    route_id VARCHAR(50) PRIMARY KEY,
    route_long_name VARCHAR(255),
    route_short_name VARCHAR(100),
    route_type INT,

    INDEX idx_routes_agency (agency_id)
);


-- ============================================
-- 3. CALENDAR
-- ============================================

CREATE TABLE IF NOT EXISTS calendar (
    service_id VARCHAR(50) PRIMARY KEY,
    start_date DATE,
    end_date DATE,
    monday TINYINT,
    tuesday TINYINT,
    wednesday TINYINT,
    thursday TINYINT,
    friday TINYINT,
    saturday TINYINT,
    sunday TINYINT
);


-- ============================================
-- 4. TRIPS
-- ============================================

CREATE TABLE IF NOT EXISTS trips (
    trip_id VARCHAR(100) PRIMARY KEY,
    route_id VARCHAR(50),
    service_id VARCHAR(50),
    shape_id VARCHAR(100),

    INDEX idx_trips_route (route_id),
    INDEX idx_trips_service (service_id)
);


-- ============================================
-- 5. STOPS
-- ============================================

CREATE TABLE IF NOT EXISTS stops (
    stop_id VARCHAR(50) PRIMARY KEY,
    stop_code VARCHAR(50),
    stop_lat DECIMAL(10,7),
    stop_lon DECIMAL(10,7),
    stop_name VARCHAR(255),
    zone_id VARCHAR(50),

    INDEX idx_stops_zone (zone_id),
    INDEX idx_stops_name (stop_name)
);


-- ============================================
-- 6. STOP TIMES
-- ============================================

CREATE TABLE IF NOT EXISTS stop_times (
    trip_id VARCHAR(100),
    arrival_time VARCHAR(20),
    departure_time VARCHAR(20),
    stop_id VARCHAR(50),
    stop_sequence INT,

    INDEX idx_stop_times_trip (trip_id),
    INDEX idx_stop_times_stop (stop_id),
    INDEX idx_stop_times_sequence (trip_id, stop_sequence)
);


-- ============================================
-- 7. FARE ATTRIBUTES
-- ============================================

CREATE TABLE IF NOT EXISTS fare_attributes (
    fare_id VARCHAR(100) PRIMARY KEY,
    price DECIMAL(10,2),
    currency_type VARCHAR(10),
    payment_method INT,
    transfers VARCHAR(20),
    agency_id VARCHAR(50),
    old_fare_id VARCHAR(100),

    INDEX idx_fare_agency (agency_id)
);


-- ============================================
-- 8. FARE RULES
-- ============================================

CREATE TABLE IF NOT EXISTS fare_rules (
    fare_id VARCHAR(100),
    route_id VARCHAR(50),
    origin_id VARCHAR(100),
    destination_id VARCHAR(100),

    INDEX idx_fare_rules_fare (fare_id),
    INDEX idx_fare_rules_route (route_id),
    INDEX idx_fare_rules_origin (origin_id),
    INDEX idx_fare_rules_destination (destination_id)
);


-- ============================================
-- VERIFY TABLES
-- ============================================

SHOW TABLES;