-- Add realistic agent memory data (successful intervention cases)
INSERT INTO agent_memory (session_id, customer_id, interaction_type, context, outcome, embedding) VALUES
('mem_001', 1, 'churn_intervention', '{"segment": "enterprise", "issue": "low_usage", "strategy": "feature_training", "success_rate": 0.89}', 'successful', '[0.1, 0.2, 0.3, 0.4, 0.5]'),
('mem_002', 3, 'churn_intervention', '{"segment": "enterprise", "issue": "billing_confusion", "strategy": "dedicated_support", "success_rate": 0.92}', 'successful', '[0.2, 0.3, 0.4, 0.5, 0.6]'),
('mem_003', 6, 'churn_intervention', '{"segment": "enterprise", "issue": "feature_requests", "strategy": "roadmap_discussion", "success_rate": 0.85}', 'successful', '[0.3, 0.4, 0.5, 0.6, 0.7]'),
('mem_004', 11, 'churn_intervention', '{"segment": "enterprise", "issue": "support_response", "strategy": "escalated_support", "success_rate": 0.88}', 'successful', '[0.4, 0.5, 0.6, 0.7, 0.8]'),
('mem_005', 14, 'churn_intervention', '{"segment": "enterprise", "issue": "integration_issues", "strategy": "technical_consultation", "success_rate": 0.91}', 'successful', '[0.5, 0.6, 0.7, 0.8, 0.9]'),
('mem_006', 18, 'churn_intervention', '{"segment": "pro", "issue": "pricing_concerns", "strategy": "discount_offer", "success_rate": 0.73}', 'successful', '[0.1, 0.3, 0.5, 0.7, 0.9]'),
('mem_007', 25, 'churn_intervention', '{"segment": "pro", "issue": "competitor_comparison", "strategy": "value_demonstration", "success_rate": 0.76}', 'successful', '[0.2, 0.4, 0.6, 0.8, 0.1]'),
('mem_008', 30, 'churn_intervention', '{"segment": "basic", "issue": "underutilization", "strategy": "onboarding_refresh", "success_rate": 0.65}', 'successful', '[0.3, 0.5, 0.7, 0.9, 0.2]'),
('mem_009', 35, 'churn_intervention', '{"segment": "basic", "issue": "complexity", "strategy": "simplified_workflow", "success_rate": 0.68}', 'successful', '[0.4, 0.6, 0.8, 0.1, 0.3]'),
('mem_010', 40, 'churn_intervention', '{"segment": "pro", "issue": "feature_gaps", "strategy": "beta_access", "success_rate": 0.81}', 'successful', '[0.5, 0.7, 0.9, 0.2, 0.4]'),
('mem_011', 42, 'churn_intervention', '{"segment": "enterprise", "issue": "performance_concerns", "strategy": "infrastructure_upgrade", "success_rate": 0.94}', 'successful', '[0.6, 0.8, 0.1, 0.3, 0.5]'),
('mem_012', 45, 'churn_intervention', '{"segment": "pro", "issue": "team_adoption", "strategy": "team_training", "success_rate": 0.79}', 'successful', '[0.7, 0.9, 0.2, 0.4, 0.6]'),
('mem_013', 48, 'churn_intervention', '{"segment": "basic", "issue": "value_unclear", "strategy": "success_metrics", "success_rate": 0.62}', 'successful', '[0.8, 0.1, 0.3, 0.5, 0.7]'),
('mem_014', 51, 'churn_intervention', '{"segment": "enterprise", "issue": "security_concerns", "strategy": "security_audit", "success_rate": 0.87}', 'successful', '[0.9, 0.2, 0.4, 0.6, 0.8]'),
('mem_015', 55, 'churn_intervention', '{"segment": "pro", "issue": "workflow_disruption", "strategy": "gradual_migration", "success_rate": 0.74}', 'successful', '[0.1, 0.4, 0.7, 0.2, 0.5]');

-- Add realistic customer communications
INSERT INTO customer_communications (customer_id, message_content, communication_type, communication_direction, sentiment_score) VALUES
-- High-risk customer communications (negative sentiment)
(2, 'We are experiencing significant issues with data synchronization. This is causing major disruptions to our daily operations and we need immediate resolution.', 'email', 'inbound', -0.7),
(4, 'The recent price increase is difficult for our budget. We are evaluating alternatives that might be more cost-effective for our organization.', 'email', 'inbound', -0.6),
(7, 'Support response times have been unacceptable lately. We submitted a critical ticket 3 days ago and still no meaningful response.', 'support_ticket', 'inbound', -0.8),
(9, 'I had a very frustrating call with support today. The representative seemed unprepared and could not resolve our billing question.', 'phone', 'inbound', -0.7),
(10, 'We are not seeing the ROI we expected from this platform. The features we need most are either missing or too complex to implement.', 'email', 'inbound', -0.5),
(12, 'System has been down twice this week during our peak hours. This is impacting our ability to serve our customers effectively.', 'chat', 'inbound', -0.8),
(15, 'The new interface is confusing and our team is struggling to adapt. We need better training resources or the old interface back.', 'email', 'inbound', -0.4),
(17, 'Competitor is offering similar features at 40% lower cost. Can you help us understand the value proposition better?', 'email', 'inbound', -0.3),
(20, 'API integration is failing frequently. Our development team is spending too much time on workarounds instead of building features.', 'support_ticket', 'inbound', -0.6),
(32, 'We have been loyal customers for 2 years but feel like we are not getting the attention we deserve. Considering other options.', 'email', 'inbound', -0.5),

-- Medium-risk customer communications (mixed sentiment)
(5, 'Overall satisfied with the platform but would like to see more reporting features. When might these be available?', 'email', 'inbound', 0.2),
(16, 'Good product but setup was more complex than expected. Would appreciate better documentation for new users.', 'email', 'inbound', 0.1),
(19, 'Love the core features but mobile app needs improvement. Any plans for mobile enhancements this year?', 'email', 'inbound', 0.3),
(36, 'Platform works well for our needs but pricing model is getting expensive as we scale. Any volume discounts available?', 'email', 'inbound', 0.0),
(38, 'Generally happy but had some issues during last weeks maintenance window. Better communication would be helpful.', 'email', 'inbound', 0.1),

-- Positive customer communications (satisfied customers)
(1, 'Excellent platform! Has significantly improved our workflow efficiency. Team loves the new dashboard features.', 'email', 'inbound', 0.8),
(3, 'Outstanding support experience. Technical team resolved our integration issue quickly and professionally.', 'email', 'inbound', 0.9),
(6, 'Platform has exceeded our expectations. ROI has been fantastic and team adoption was seamless.', 'email', 'inbound', 0.9),
(11, 'Very impressed with the recent feature updates. Exactly what we needed for our expanding operations.', 'email', 'inbound', 0.7),
(14, 'Best decision we made this year was switching to your platform. Highly recommend to other companies in our space.', 'email', 'inbound', 0.9),
(21, 'Great product and even better support. Your team has been incredibly responsive to our needs.', 'email', 'inbound', 0.8),
(24, 'Platform stability has been excellent. No downtime issues and performance is consistently good.', 'email', 'inbound', 0.7),
(27, 'Integration was smooth and your technical documentation is top-notch. Made implementation much easier than expected.', 'email', 'inbound', 0.8),
(40, 'Fantastic value for money. Feature set keeps improving and support quality remains high.', 'email', 'inbound', 0.8),
(45, 'Platform has become essential to our operations. Could not imagine running our business without it now.', 'email', 'inbound', 0.9);

-- Add some retention patterns based on successful interventions
INSERT INTO retention_patterns (pattern_name, customer_characteristics, successful_interventions, success_rate, customer_segment, churn_reason_category, embedding) VALUES
('enterprise_billing_support', '{"avg_revenue": 120000, "avg_usage": 0.7, "common_issues": ["billing_complexity", "invoice_questions"]}', '["dedicated_billing_support", "billing_walkthrough", "automated_invoicing"]', 0.89, 'enterprise', 'billing_issues', '[0.1, 0.2, 0.3, 0.4, 0.5]'),
('pro_feature_adoption', '{"avg_revenue": 30000, "avg_usage": 0.4, "common_issues": ["feature_discovery", "training_needs"]}', '["feature_training", "success_coaching", "implementation_support"]', 0.76, 'pro', 'underutilization', '[0.2, 0.3, 0.4, 0.5, 0.6]'),
('basic_value_realization', '{"avg_revenue": 10000, "avg_usage": 0.3, "common_issues": ["complexity", "unclear_value"]}', '["simplified_onboarding", "quick_wins", "success_metrics"]', 0.64, 'basic', 'value_concerns', '[0.3, 0.4, 0.5, 0.6, 0.7]'),
('enterprise_technical_escalation', '{"avg_revenue": 150000, "avg_usage": 0.8, "common_issues": ["performance", "integration", "security"]}', '["technical_escalation", "architecture_review", "dedicated_engineer"]', 0.92, 'enterprise', 'technical_issues', '[0.4, 0.5, 0.6, 0.7, 0.8]'),
('startup_budget_constraints', '{"avg_revenue": 8000, "avg_usage": 0.6, "common_issues": ["pricing", "budget", "growth_concerns"]}', '["startup_discount", "flexible_pricing", "growth_plan"]', 0.71, 'basic', 'pricing_concerns', '[0.5, 0.6, 0.7, 0.8, 0.9]'),
('midmarket_competitor_threat', '{"avg_revenue": 50000, "avg_usage": 0.5, "common_issues": ["competitor_offers", "feature_parity"]}', '["competitive_analysis", "roadmap_preview", "executive_call"]', 0.78, 'pro', 'competitive_pressure', '[0.6, 0.7, 0.8, 0.9, 0.1]'),
('healthcare_compliance_needs', '{"avg_revenue": 80000, "avg_usage": 0.7, "common_issues": ["compliance", "security", "audit_support"]}', '["compliance_consultation", "security_review", "audit_assistance"]', 0.85, 'enterprise', 'compliance_concerns', '[0.7, 0.8, 0.9, 0.1, 0.2]'),
('international_support_gaps', '{"avg_revenue": 40000, "avg_usage": 0.6, "common_issues": ["timezone_support", "localization"]}', '["extended_support_hours", "local_contact", "regional_training"]', 0.72, 'pro', 'support_issues', '[0.8, 0.9, 0.1, 0.2, 0.3]');
