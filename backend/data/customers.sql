INSERT INTO customers (
    name, email, company, subscription_plan, monthly_revenue, annual_contract_value,
    days_since_signup, last_login_days_ago, support_tickets_count, 
    feature_usage_score, nps_score, payment_delays, 
    churn_probability, churn_risk_level, phone, timezone, preferred_contact,
    behavior_embedding, usage_patterns
) VALUES 
(
    'Marcus Crisis', 
    'marcus@crisis-corp.com', 
    'Crisis Corporation', 
    'enterprise', 
    7500, 
    90000,
    120, 
    18, 
    15, 
    0.15, 
    3, 
    2,
    0.94, 
    'critical',
    '+1-555-0999',
    'America/New_York',
    'phone',
    '[0.1, 0.15, 0.3, 0.85, 0.2, 1.0]',
    '{"daily_logins": 1, "features_used": 3, "time_spent_minutes": 25}'
),
(
    'Diana Emergency', 
    'diana@urgent-solutions.com', 
    'Urgent Solutions Ltd', 
    'pro', 
    3200, 
    38400,
    90, 
    21, 
    12, 
    0.18, 
    4, 
    3,
    0.91, 
    'critical',
    '+1-555-0888',
    'America/Los_Angeles',
    'email',
    '[0.18, 0.18, 0.4, 0.82, 0.15, 0.7]',
    '{"daily_logins": 0, "features_used": 2, "time_spent_minutes": 15}'
);

INSERT INTO customers (name, email, company, subscription_plan, monthly_revenue, annual_contract_value, 
                      days_since_signup, last_login_days_ago, support_tickets_count, feature_usage_score, 
                      nps_score, payment_delays, phone, timezone, preferred_contact, churn_probability, churn_risk_level) VALUES

-- High-tech companies
('Alex Chen', 'alex@techflow.com', 'TechFlow Solutions', 'enterprise', 8900, 106800, 180, 2, 1, 0.85, 9, 0, '+1-555-1001', 'America/Los_Angeles', 'email', 0.25, 'low'),
('Sarah Rodriguez', 'sarah@datastream.io', 'DataStream Analytics', 'pro', 1899, 22788, 45, 15, 8, 0.35, 5, 2, '+1-555-1002', 'America/New_York', 'phone', 0.78, 'high'),
('Mike Johnson', 'mike@cloudforge.com', 'CloudForge Inc', 'enterprise', 12500, 150000, 320, 1, 0, 0.92, 10, 0, '+1-555-1003', 'America/Chicago', 'email', 0.15, 'low'),
('Emma Wilson', 'emma@aiventures.com', 'AI Ventures', 'pro', 2299, 27588, 89, 22, 12, 0.28, 4, 3, '+1-555-1004', 'America/Los_Angeles', 'email', 0.85, 'critical'),
('David Park', 'david@scaletech.net', 'ScaleTech Networks', 'basic', 699, 8388, 150, 5, 3, 0.65, 7, 1, '+1-555-1005', 'America/New_York', 'phone', 0.45, 'medium'),

-- Financial services
('Jennifer Walsh', 'j.walsh@finnovate.com', 'FinNovate Corp', 'enterprise', 15600, 187200, 240, 3, 2, 0.78, 8, 0, '+1-555-1006', 'America/New_York', 'email', 0.32, 'low'),
('Robert Kim', 'robert@investwise.com', 'InvestWise Partners', 'pro', 3299, 39588, 67, 18, 9, 0.42, 6, 1, '+1-555-1007', 'America/Chicago', 'email', 0.72, 'high'),
('Lisa Thompson', 'lisa@capitalflow.io', 'CapitalFlow Solutions', 'enterprise', 9800, 117600, 195, 7, 4, 0.71, 8, 0, '+1-555-1008', 'America/Los_Angeles', 'phone', 0.38, 'low'),
('James Martinez', 'james@tradepro.com', 'TradePro Analytics', 'basic', 899, 10788, 78, 25, 15, 0.22, 3, 4, '+1-555-1009', 'America/New_York', 'email', 0.91, 'critical'),
('Maria Garcia', 'maria@wealthtech.com', 'WealthTech Innovations', 'pro', 2799, 33588, 112, 12, 6, 0.58, 7, 2, '+1-555-1010', 'America/Chicago', 'email', 0.64, 'high'),

-- Healthcare companies
('Dr. Amanda Foster', 'amanda@healthflow.com', 'HealthFlow Systems', 'enterprise', 11200, 134400, 290, 4, 3, 0.82, 9, 0, '+1-555-1011', 'America/Los_Angeles', 'phone', 0.28, 'low'),
('Dr. Kevin Brown', 'kevin@medtech.io', 'MedTech Solutions', 'pro', 2899, 34788, 156, 21, 11, 0.31, 5, 3, '+1-555-1012', 'America/New_York', 'email', 0.81, 'critical'),
('Rachel Green', 'rachel@careconnect.com', 'CareConnect Platform', 'basic', 1299, 15588, 89, 14, 7, 0.48, 6, 1, '+1-555-1013', 'America/Chicago', 'email', 0.69, 'high'),
('Dr. Thomas Lee', 'thomas@healthdata.com', 'HealthData Corp', 'enterprise', 14300, 171600, 245, 2, 1, 0.89, 9, 0, '+1-555-1014', 'America/Los_Angeles', 'email', 0.22, 'low'),
('Nancy Davis', 'nancy@medanalytics.com', 'MedAnalytics Inc', 'pro', 1999, 23988, 134, 16, 8, 0.44, 6, 2, '+1-555-1015', 'America/New_York', 'phone', 0.73, 'high'),

-- E-commerce companies
('Tom Wilson', 'tom@ecommflow.com', 'EcommFlow Solutions', 'basic', 599, 7188, 67, 8, 4, 0.62, 7, 1, '+1-555-1016', 'America/Chicago', 'email', 0.52, 'medium'),
('Sophie Chen', 'sophie@retailtech.io', 'RetailTech Innovations', 'pro', 2599, 31188, 98, 19, 10, 0.37, 5, 2, '+1-555-1017', 'America/Los_Angeles', 'email', 0.76, 'high'),
('Michael Davis', 'michael@shopstream.com', 'ShopStream Analytics', 'enterprise', 7800, 93600, 178, 6, 2, 0.73, 8, 0, '+1-555-1018', 'America/New_York', 'phone', 0.41, 'medium'),
('Christina Wang', 'christina@marketflow.com', 'MarketFlow Platform', 'basic', 799, 9588, 123, 11, 5, 0.55, 7, 1, '+1-555-1019', 'America/Chicago', 'email', 0.58, 'medium'),
('Daniel Kim', 'daniel@commerceai.com', 'CommerceAI Corp', 'pro', 3199, 38388, 156, 23, 13, 0.29, 4, 3, '+1-555-1020', 'America/Los_Angeles', 'email', 0.84, 'critical'),

-- Manufacturing companies
('Karen Johnson', 'karen@manuflow.com', 'ManufFlow Systems', 'enterprise', 13400, 160800, 267, 5, 3, 0.76, 8, 0, '+1-555-1021', 'America/Chicago', 'phone', 0.35, 'low'),
('Steve Rodriguez', 'steve@industech.com', 'IndusTech Solutions', 'pro', 2399, 28788, 145, 17, 9, 0.41, 6, 2, '+1-555-1022', 'America/New_York', 'email', 0.71, 'high'),
('Laura Martinez', 'laura@factoryai.com', 'FactoryAI Inc', 'basic', 1099, 13188, 98, 13, 6, 0.51, 6, 1, '+1-555-1023', 'America/Los_Angeles', 'email', 0.62, 'high'),
('Paul Wilson', 'paul@smartmanuf.com', 'SmartManuf Corp', 'enterprise', 16800, 201600, 312, 3, 1, 0.87, 9, 0, '+1-555-1024', 'America/Chicago', 'email', 0.19, 'low'),
('Michelle Brown', 'michelle@prodflow.com', 'ProdFlow Analytics', 'pro', 2799, 33588, 178, 20, 11, 0.34, 5, 3, '+1-555-1025', 'America/New_York', 'phone', 0.79, 'high'),

-- Education companies
('Prof. John Smith', 'john@edutech.com', 'EduTech Innovations', 'pro', 1899, 22788, 123, 9, 4, 0.67, 8, 1, '+1-555-1026', 'America/Los_Angeles', 'email', 0.48, 'medium'),
('Dr. Susan Lee', 'susan@learnflow.com', 'LearnFlow Platform', 'basic', 899, 10788, 89, 15, 7, 0.43, 6, 2, '+1-555-1027', 'America/New_York', 'email', 0.68, 'high'),
('Mark Thompson', 'mark@smartedu.io', 'SmartEdu Solutions', 'enterprise', 8900, 106800, 234, 4, 2, 0.81, 9, 0, '+1-555-1028', 'America/Chicago', 'phone', 0.31, 'low'),
('Elena Garcia', 'elena@skilltech.com', 'SkillTech Corp', 'pro', 2199, 26388, 156, 18, 8, 0.39, 5, 2, '+1-555-1029', 'America/Los_Angeles', 'email', 0.74, 'high'),
('Ryan Davis', 'ryan@knowledgeai.com', 'KnowledgeAI Inc', 'basic', 699, 8388, 67, 12, 5, 0.56, 7, 1, '+1-555-1030', 'America/New_York', 'email', 0.57, 'medium'),

-- Startups with varying risk levels
('Zoe Chen', 'zoe@startupflow.com', 'StartupFlow Accelerator', 'basic', 499, 5988, 34, 28, 18, 0.18, 3, 5, '+1-555-1031', 'America/Los_Angeles', 'email', 0.93, 'critical'),
('Alex Rivera', 'alex@innovatelab.com', 'InnovateLab Studio', 'pro', 1599, 19188, 78, 24, 14, 0.26, 4, 4, '+1-555-1032', 'America/New_York', 'phone', 0.87, 'critical'),
('Jordan Kim', 'jordan@techlaunch.io', 'TechLaunch Ventures', 'basic', 799, 9588, 45, 26, 16, 0.21, 3, 4, '+1-555-1033', 'America/Chicago', 'email', 0.89, 'critical'),
('Casey Wong', 'casey@futuretech.com', 'FutureTech Labs', 'pro', 2099, 25188, 89, 22, 12, 0.33, 4, 3, '+1-555-1034', 'America/Los_Angeles', 'email', 0.82, 'critical'),
('Morgan Davis', 'morgan@visionai.com', 'VisionAI Startup', 'basic', 899, 10788, 56, 27, 17, 0.19, 3, 5, '+1-555-1035', 'America/New_York', 'email', 0.91, 'critical'),

-- Medium-sized businesses
('Helen Rodriguez', 'helen@bizflow.com', 'BizFlow Solutions', 'pro', 2399, 28788, 167, 10, 5, 0.63, 7, 1, '+1-555-1036', 'America/Chicago', 'phone', 0.49, 'medium'),
('Carlos Martinez', 'carlos@growthhub.com', 'GrowthHub Analytics', 'enterprise', 9200, 110400, 198, 7, 3, 0.74, 8, 0, '+1-555-1037', 'America/Los_Angeles', 'email', 0.37, 'low'),
('Diana Park', 'diana@scaleup.io', 'ScaleUp Platform', 'pro', 2799, 33588, 134, 14, 6, 0.57, 7, 2, '+1-555-1038', 'America/New_York', 'email', 0.61, 'high'),
('Frank Wilson', 'frank@midmarket.com', 'MidMarket Corp', 'basic', 1299, 15588, 123, 11, 4, 0.59, 7, 1, '+1-555-1039', 'America/Chicago', 'email', 0.54, 'medium'),
('Grace Kim', 'grace@businessai.com', 'BusinessAI Solutions', 'enterprise', 11800, 141600, 223, 5, 2, 0.79, 8, 0, '+1-555-1040', 'America/Los_Angeles', 'phone', 0.33, 'low'),

-- International companies
('Hans Mueller', 'hans@eurotech.de', 'EuroTech GmbH', 'enterprise', 14500, 174000, 298, 6, 2, 0.83, 9, 0, '+49-30-12345678', 'Europe/Berlin', 'email', 0.27, 'low'),
('Yuki Tanaka', 'yuki@japanflow.jp', 'JapanFlow KK', 'pro', 2899, 34788, 187, 19, 9, 0.38, 5, 2, '+81-3-1234-5678', 'Asia/Tokyo', 'email', 0.75, 'high'),
('Pierre Dubois', 'pierre@frenchtech.fr', 'FrenchTech Solutions', 'basic', 1199, 14388, 145, 16, 8, 0.45, 6, 2, '+33-1-23-45-67-89', 'Europe/Paris', 'phone', 0.67, 'high'),
('Emma Johnson', 'emma@ukdata.co.uk', 'UK Data Analytics', 'enterprise', 12300, 147600, 267, 4, 1, 0.86, 9, 0, '+44-20-1234-5678', 'Europe/London', 'email', 0.24, 'low'),
('Marco Rossi', 'marco@italytech.it', 'ItalyTech SpA', 'pro', 2299, 27588, 156, 17, 7, 0.42, 6, 2, '+39-06-1234-5678', 'Europe/Rome', 'email', 0.72, 'high'),

-- Additional diverse companies to reach 50+ customers
('Tyler Anderson', 'tyler@cloudnative.io', 'CloudNative Systems', 'enterprise', 15900, 190800, 345, 2, 0, 0.91, 10, 0, '+1-555-1045', 'America/Los_Angeles', 'email', 0.16, 'low'),
('Samantha Lee', 'sam@dataops.com', 'DataOps Corporation', 'pro', 3199, 38388, 189, 21, 10, 0.35, 5, 3, '+1-555-1046', 'America/New_York', 'phone', 0.77, 'high'),
('Benjamin Clark', 'ben@devtools.io', 'DevTools Innovations', 'basic', 999, 11988, 78, 25, 15, 0.24, 4, 4, '+1-555-1047', 'America/Chicago', 'email', 0.88, 'critical'),
('Olivia Turner', 'olivia@securetech.com', 'SecureTech Solutions', 'enterprise', 13700, 164400, 278, 3, 1, 0.88, 9, 0, '+1-555-1048', 'America/Los_Angeles', 'email', 0.21, 'low'),
('Nathan Brooks', 'nathan@aiplatform.io', 'AI Platform Corp', 'pro', 2699, 32388, 167, 20, 11, 0.32, 4, 3, '+1-555-1049', 'America/New_York', 'email', 0.83, 'critical');

-- Add more customers to reach 60+ total
INSERT INTO customers (name, email, company, subscription_plan, monthly_revenue, annual_contract_value, 
                      days_since_signup, last_login_days_ago, support_tickets_count, feature_usage_score, 
                      nps_score, payment_delays, phone, timezone, preferred_contact, churn_probability, churn_risk_level) VALUES

('Isabella Rodriguez', 'isabella@finflow.com', 'FinFlow Technologies', 'pro', 2899, 34788, 134, 18, 9, 0.36, 5, 2, '+1-555-1050', 'America/Chicago', 'email', 0.78, 'high'),
('Ethan Wilson', 'ethan@techstream.io', 'TechStream Analytics', 'basic', 1199, 14388, 89, 23, 13, 0.27, 4, 3, '+1-555-1051', 'America/Los_Angeles', 'phone', 0.86, 'critical'),
('Sophia Davis', 'sophia@innovflow.com', 'InnovFlow Solutions', 'enterprise', 16200, 194400, 356, 1, 0, 0.94, 10, 0, '+1-555-1052', 'America/New_York', 'email', 0.12, 'low'),
('Mason Garcia', 'mason@startupai.com', 'StartupAI Labs', 'basic', 699, 8388, 45, 29, 19, 0.16, 2, 5, '+1-555-1053', 'America/Chicago', 'email', 0.95, 'critical'),
('Ava Martinez', 'ava@growthtech.io', 'GrowthTech Platform', 'pro', 2399, 28788, 178, 15, 7, 0.48, 6, 2, '+1-555-1054', 'America/Los_Angeles', 'email', 0.66, 'high'),
('Logan Brown', 'logan@scaleflow.com', 'ScaleFlow Corporation', 'enterprise', 11900, 142800, 234, 8, 4, 0.72, 8, 1, '+1-555-1055', 'America/New_York', 'phone', 0.39, 'low'),
('Mia Johnson', 'mia@techventure.io', 'TechVenture Inc', 'basic', 899, 10788, 67, 24, 14, 0.23, 3, 4, '+1-555-1056', 'America/Chicago', 'email', 0.87, 'critical'),
('Lucas Kim', 'lucas@cloudflow.com', 'CloudFlow Systems', 'pro', 3099, 37188, 156, 19, 10, 0.41, 5, 2, '+1-555-1057', 'America/Los_Angeles', 'email', 0.74, 'high'),
('Charlotte Lee', 'charlotte@datatech.io', 'DataTech Solutions', 'enterprise', 14800, 177600, 289, 5, 2, 0.84, 9, 0, '+1-555-1058', 'America/New_York', 'email', 0.26, 'low'),
('Owen Taylor', 'owen@innovateai.com', 'InnovateAI Corp', 'basic', 1099, 13188, 78, 26, 16, 0.20, 3, 4, '+1-555-1059', 'America/Chicago', 'phone', 0.90, 'critical');

