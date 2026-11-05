// === Groupware Architecture B Graph DDL / DML ===
// Constraints
CREATE CONSTRAINT c_tenant_id IF NOT EXISTS FOR (t:Tenant) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT c_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT c_dept_id IF NOT EXISTS FOR (d:Department) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT c_conv_id IF NOT EXISTS FOR (c:ChatConversation) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT c_notice_id IF NOT EXISTS FOR (n:Notice) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT c_audience_id IF NOT EXISTS FOR (a:Audience) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT c_project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT c_approval_id IF NOT EXISTS FOR (app:ApprovalRequest) REQUIRE app.id IS UNIQUE;
CREATE CONSTRAINT c_asset_id IF NOT EXISTS FOR (ast:Asset) REQUIRE ast.id IS UNIQUE;
CREATE CONSTRAINT c_asset_cat_id IF NOT EXISTS FOR (ac:AssetCategory) REQUIRE ac.id IS UNIQUE;

// Load Tenant Nodes
MERGE (n:Tenant {id: 1}) SET n += {name: "Tenant Alpha", domain: "", is_active: true, is_deleted: false};
MERGE (n:Tenant {id: 2}) SET n += {name: "Tenant Beta", domain: "", is_active: true, is_deleted: false};

// Load User Nodes
MERGE (n:User {id: 101}) SET n += {tenant_id: 1, username: "alice.t1", email: "alice@alpha.com", status: "ACTIVE", is_deleted: false};
MERGE (n:User {id: 102}) SET n += {tenant_id: 1, username: "bob.suspended", email: "bob@alpha.com", status: "ACTIVE", is_deleted: false};
MERGE (n:User {id: 103}) SET n += {tenant_id: 1, username: "charlie.deleted_mem", email: "charlie@alpha.com", status: "ACTIVE", is_deleted: false};
MERGE (n:User {id: 104}) SET n += {tenant_id: 2, username: "david.multi", email: "david@both.com", status: "ACTIVE", is_deleted: false};
MERGE (n:User {id: 105}) SET n += {tenant_id: 2, username: "eve.both", email: "eve@both.com", status: "ACTIVE", is_deleted: false};
MERGE (n:User {id: 106}) SET n += {tenant_id: 1, username: "frank.inactive", email: "frank@alpha.com", status: "ACTIVE", is_deleted: false};
MERGE (n:User {id: 107}) SET n += {tenant_id: 1, username: "ivan.deleted_user", email: "ivan@alpha.com", status: "ACTIVE", is_deleted: true};
MERGE (n:User {id: 108}) SET n += {tenant_id: 1, username: "judy.pure", email: "judy@alpha.com", status: "ACTIVE", is_deleted: false};
MERGE (n:User {id: 201}) SET n += {tenant_id: 2, username: "grace.t2", email: "grace@beta.com", status: "ACTIVE", is_deleted: false};
MERGE (n:User {id: 202}) SET n += {tenant_id: 2, username: "heidi.t2_mgr", email: "heidi@beta.com", status: "ACTIVE", is_deleted: false};

// Load Department Nodes
MERGE (n:Department {id: 10}) SET n += {tenant_id: 1, name: "Engineering Alpha", code: "ENG-T1", is_deleted: false};
MERGE (n:Department {id: 11}) SET n += {tenant_id: 1, name: "QA Alpha (Suspended Mgr)", code: "QA-T1", is_deleted: false};
MERGE (n:Department {id: 12}) SET n += {tenant_id: 1, name: "Ops Alpha (Cross-Tenant Mgr)", code: "OPS-T1", is_deleted: false};
MERGE (n:Department {id: 13}) SET n += {tenant_id: 1, name: "Finance Alpha (Inactive Mgr)", code: "FIN-T1", is_deleted: false};
MERGE (n:Department {id: 14}) SET n += {tenant_id: 1, name: "HR Alpha (Deleted User Mgr)", code: "HR-T1", is_deleted: false};
MERGE (n:Department {id: 15}) SET n += {tenant_id: 1, name: "Legal Alpha (Deleted Mem Mgr)", code: "LEG-T1", is_deleted: false};
MERGE (n:Department {id: 16}) SET n += {tenant_id: 1, name: "Empty Alpha (0 Sub, 0 Emp)", code: "EMPTY-T1", is_deleted: false};
MERGE (n:Department {id: 17}) SET n += {tenant_id: 1, name: "Leaf Alpha (0 Sub, Has Emp)", code: "LEAF-T1", is_deleted: false};
MERGE (n:Department {id: 20}) SET n += {tenant_id: 2, name: "Engineering Beta", code: "ENG-T2", is_deleted: false};
MERGE (n:Department {id: 21}) SET n += {tenant_id: 2, name: "QA Beta", code: "QA-T2", is_deleted: false};

// Load ChatConversation Nodes
MERGE (n:ChatConversation {id: "conv_101"}) SET n += {tenant_id: 1, title: "Ph\u00f2ng K\u1ef9 thu\u1eadt & Ph\u00e1t tri\u1ec3n AI", conversation_type: "group", is_deleted: false};
MERGE (n:ChatConversation {id: "conv_102"}) SET n += {tenant_id: 1, title: "Ban Gi\u00e1m \u0111\u1ed1c & Ph\u00ea duy\u1ec7t", conversation_type: "private", is_deleted: false};
MERGE (n:ChatConversation {id: "conv_201"}) SET n += {tenant_id: 2, title: "C\u00f4ng ty T2 - K\u1ebf to\u00e1n & T\u00e0i ch\u00ednh", conversation_type: "group", is_deleted: false};

// Load Notice Nodes
MERGE (n:Notice {id: 901}) SET n += {tenant_id: 1, title: "T1 Global Notice Valid", notice_type: "general", priority: "high", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 902}) SET n += {tenant_id: 1, title: "T1 Custom Notice Valid", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 903}) SET n += {tenant_id: 1, title: "T1 Notice with T2 Audience (Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 904}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 4 (Owner T1, User T1, Dept T2 - Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 905}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 5 (Owner T1, User T2, Dept T1 - Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 906}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 6 (Owner T2, User T1, Dept T1 - Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 907}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 7 (Mixed Memberships - Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 908}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 8 (Missing Valid Owner - Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 909}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 9 (Global with Owner - Deny)", notice_type: "general", priority: "high", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 910}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 10 (Global with Tenant - Deny)", notice_type: "general", priority: "high", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 911}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 11 (Global with Dept - Deny)", notice_type: "general", priority: "high", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 912}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 12 (Global with User - Deny)", notice_type: "general", priority: "high", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 913}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 13 (Global Type Custom - Deny)", notice_type: "general", priority: "high", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 914}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 14 (Deleted Dept Member - Exclude/Allow)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 915}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 15 (Deleted User Member - Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 916}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 16 (Multi-tenant User - Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 917}) SET n += {tenant_id: 2, title: "T2 Notice in T1 Query (Cross-Tenant - Deny)", notice_type: "general", priority: "high", is_published: true, is_deleted: false};
MERGE (n:Notice {id: 918}) SET n += {tenant_id: 1, title: "T1 Notice with Aud 18 (Invalid Dept Ref - Deny)", notice_type: "dept", priority: "normal", is_published: true, is_deleted: false};

// Load Audience Nodes
MERGE (n:Audience {id: 1}) SET n += {tenant_id: null, name: "All Company (Valid Global)", is_system: true, is_deleted: false};
MERGE (n:Audience {id: 2}) SET n += {tenant_id: 1, name: "T1 Pure Custom Audience", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 3}) SET n += {tenant_id: 2, name: "T2 Pure Custom Audience", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 4}) SET n += {tenant_id: null, name: "Vuln: Owner T1, User T1, Dept T2", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 5}) SET n += {tenant_id: null, name: "Vuln: Owner T1, User T2, Dept T1", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 6}) SET n += {tenant_id: null, name: "Vuln: Owner T2, User T1, Dept T1", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 7}) SET n += {tenant_id: null, name: "Mixed Memberships T1 & T2", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 8}) SET n += {tenant_id: null, name: "Missing Valid Owner (Suspended)", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 9}) SET n += {tenant_id: null, name: "Global Audience with Owner (Invalid)", is_system: true, is_deleted: false};
MERGE (n:Audience {id: 10}) SET n += {tenant_id: 1, name: "Global Audience with Tenant (Invalid)", is_system: true, is_deleted: false};
MERGE (n:Audience {id: 11}) SET n += {tenant_id: null, name: "Global Audience with Dept Members (Invalid)", is_system: true, is_deleted: false};
MERGE (n:Audience {id: 12}) SET n += {tenant_id: null, name: "Global Audience with User Members (Invalid)", is_system: true, is_deleted: false};
MERGE (n:Audience {id: 13}) SET n += {tenant_id: null, name: "Global Audience Type Custom (Invalid)", is_system: true, is_deleted: false};
MERGE (n:Audience {id: 14}) SET n += {tenant_id: 1, name: "Custom with Ended Dept Member", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 15}) SET n += {tenant_id: 1, name: "Custom with Deleted User Member", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 16}) SET n += {tenant_id: 1, name: "Custom with Multi-Tenant User Member", is_system: false, is_deleted: false};
MERGE (n:Audience {id: 18}) SET n += {tenant_id: 1, name: "Custom with Invalid Dept Ref (999)", is_system: false, is_deleted: false};

// Load Project Nodes
MERGE (n:Project {id: "proj_01"}) SET n += {tenant_id: 1, name: "AI Chatbot Groupware", code: "PRJ-AIC", status: "IN_PROGRESS", is_deleted: false};
MERGE (n:Project {id: "proj_02"}) SET n += {tenant_id: 2, name: "H\u1ec7 th\u1ed1ng ERP Tenant 2", code: "PRJ-ERP", status: "PLANNING", is_deleted: false};

// Load ApprovalRequest Nodes
MERGE (n:ApprovalRequest {id: "appr_01"}) SET n += {tenant_id: 1, title: "\u0110\u1ec1 xu\u1ea5t mua s\u1eafm m\u00e1y ch\u1ee7 GPU ph\u1ee5c v\u1ee5 hu\u1ea5n luy\u1ec7n m\u00f4 h\u00ecnh", status: "APPROVED", is_deleted: false};
MERGE (n:ApprovalRequest {id: "appr_02"}) SET n += {tenant_id: 2, title: "Y\u00eau c\u1ea7u c\u1ea5p ph\u00e1t t\u00e0i s\u1ea3n m\u00e1y t\u00ednh x\u00e1ch tay Dell XPS", status: "PENDING", is_deleted: false};

// Load AssetCategory Nodes
MERGE (n:AssetCategory {id: 1}) SET n += {code: "LAPTOP", name: "M\u00e1y t\u00ednh x\u00e1ch tay (Laptop)", is_active: true};
MERGE (n:AssetCategory {id: 2}) SET n += {code: "SERVER", name: "M\u00e1y ch\u1ee7 & Thi\u1ebft b\u1ecb m\u1ea1ng", is_active: true};
MERGE (n:AssetCategory {id: 3}) SET n += {code: "OFFICE_FURNITURE", name: "N\u1ed9i th\u1ea5t v\u0103n ph\u00f2ng", is_active: true};
MERGE (n:AssetCategory {id: 4}) SET n += {code: "VEHICLE", name: "Ph\u01b0\u01a1ng ti\u1ec7n v\u1eadn t\u1ea3i", is_active: true};

// Load Asset Nodes
MERGE (n:Asset {id: 1001}) SET n += {tenant_id: 1, asset_code: "AST-T1-LP-01", name: "MacBook Pro M3 Max 36GB", status: "IN_USE", serial_number: "C02XYZ123456", is_deleted: false};
MERGE (n:Asset {id: 1002}) SET n += {tenant_id: 1, asset_code: "AST-T1-SRV-01", name: "GPU Server Dell PowerEdge R750 4x A100", status: "ACTIVE", serial_number: "SRV-DELL-8899", is_deleted: false};
MERGE (n:Asset {id: 1003}) SET n += {tenant_id: 1, asset_code: "AST-T1-LP-02", name: "ThinkPad T14s Gen 4 i7 32GB", status: "IN_USE", serial_number: "PF-2XYZ7788", is_deleted: false};
MERGE (n:Asset {id: 2001}) SET n += {tenant_id: 2, asset_code: "AST-T2-LP-01", name: "Dell XPS 15 9530 i9 64GB", status: "IN_USE", serial_number: "DELL-XPS-9900", is_deleted: false};
MERGE (n:Asset {id: 2002}) SET n += {tenant_id: 2, asset_code: "AST-T2-CAR-01", name: "Xe \u00f4 t\u00f4 \u0111\u01b0a \u0111\u00f3n l\u00e3nh \u0111\u1ea1o Toyota Camry", status: "IN_USE", serial_number: "29A-888.88", is_deleted: false};

// Load Relationships
MATCH (s:User {id: 101}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 102}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 103}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 104}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:User {id: 105}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:User {id: 106}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 107}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 108}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 201}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:User {id: 202}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Department {id: 10}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Department {id: 11}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Department {id: 12}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Department {id: 13}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Department {id: 14}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Department {id: 15}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Department {id: 16}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Department {id: 17}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Department {id: 20}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Department {id: 21}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:User {id: 101}), (t:Department {id: 10}) MERGE (s)-[r:MEMBER_OF]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 105}), (t:Department {id: 10}) MERGE (s)-[r:MEMBER_OF]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 104}), (t:Department {id: 10}) MERGE (s)-[r:MEMBER_OF]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 102}), (t:Department {id: 10}) MERGE (s)-[r:MEMBER_OF]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 101}), (t:Department {id: 17}) MERGE (s)-[r:MEMBER_OF]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 201}), (t:Department {id: 20}) MERGE (s)-[r:MEMBER_OF]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:User {id: 202}), (t:Department {id: 20}) MERGE (s)-[r:MEMBER_OF]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:User {id: 108}), (t:Department {id: 10}) MERGE (s)-[r:MEMBER_OF]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 901}), (t:Audience {id: 1}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 901}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 902}), (t:Audience {id: 2}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 902}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 903}), (t:Audience {id: 3}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 903}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 904}), (t:Audience {id: 4}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 904}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 905}), (t:Audience {id: 5}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 905}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 906}), (t:Audience {id: 6}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 906}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 907}), (t:Audience {id: 7}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 907}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 908}), (t:Audience {id: 8}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 908}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 909}), (t:Audience {id: 9}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 909}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 910}), (t:Audience {id: 10}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 910}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 911}), (t:Audience {id: 11}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 911}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 912}), (t:Audience {id: 12}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 912}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 913}), (t:Audience {id: 13}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 913}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 914}), (t:Audience {id: 14}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 914}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 915}), (t:Audience {id: 15}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 915}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 916}), (t:Audience {id: 16}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 916}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 917}), (t:Audience {id: 1}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Notice {id: 917}), (t:User {id: 202}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Notice {id: 918}), (t:Audience {id: 18}) MERGE (s)-[r:TARGETS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Notice {id: 918}), (t:User {id: 101}) MERGE (s)-[r:CREATED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:ChatConversation {id: "conv_101"}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 101}), (t:ChatConversation {id: "conv_101"}) MERGE (s)-[r:PARTICIPATES_IN]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:ChatConversation {id: "conv_102"}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:User {id: 102}), (t:ChatConversation {id: "conv_102"}) MERGE (s)-[r:PARTICIPATES_IN]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:ChatConversation {id: "conv_201"}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:User {id: 201}), (t:ChatConversation {id: "conv_201"}) MERGE (s)-[r:PARTICIPATES_IN]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Project {id: "proj_01"}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Project {id: "proj_02"}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:ApprovalRequest {id: "appr_01"}), (t:User {id: 101}) MERGE (s)-[r:REQUESTED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:ApprovalRequest {id: "appr_02"}), (t:User {id: 201}) MERGE (s)-[r:REQUESTED_BY]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Asset {id: 1001}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1001}), (t:AssetCategory {id: 1}) MERGE (s)-[r:CATEGORIZED_AS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1001}), (t:User {id: 101}) MERGE (s)-[r:ASSIGNED_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1001}), (t:Department {id: 1}) MERGE (s)-[r:LOCATED_IN]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1002}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1002}), (t:AssetCategory {id: 2}) MERGE (s)-[r:CATEGORIZED_AS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1002}), (t:User {id: 102}) MERGE (s)-[r:ASSIGNED_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1002}), (t:Department {id: 1}) MERGE (s)-[r:LOCATED_IN]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1003}), (t:Tenant {id: 1}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1003}), (t:AssetCategory {id: 1}) MERGE (s)-[r:CATEGORIZED_AS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1003}), (t:User {id: 103}) MERGE (s)-[r:ASSIGNED_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 1003}), (t:Department {id: 2}) MERGE (s)-[r:LOCATED_IN]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 1;
MATCH (s:Asset {id: 2001}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Asset {id: 2001}), (t:AssetCategory {id: 1}) MERGE (s)-[r:CATEGORIZED_AS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Asset {id: 2001}), (t:User {id: 201}) MERGE (s)-[r:ASSIGNED_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Asset {id: 2001}), (t:Department {id: 3}) MERGE (s)-[r:LOCATED_IN]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Asset {id: 2002}), (t:Tenant {id: 2}) MERGE (s)-[r:BELONGS_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Asset {id: 2002}), (t:AssetCategory {id: 4}) MERGE (s)-[r:CATEGORIZED_AS]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Asset {id: 2002}), (t:User {id: 202}) MERGE (s)-[r:ASSIGNED_TO]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
MATCH (s:Asset {id: 2002}), (t:Department {id: 3}) MERGE (s)-[r:LOCATED_IN]->(t) ON CREATE SET r.created_at = datetime(), r.tenant_id = 2;
