-- ===============================================================
-- CampusConnect - Smart Lost and Found Management System
-- Institution: VSIT (Vidyalankar School of Information Technology)
-- Database: SQLite3 Relational Database Schema & Demo Seed Data
-- Generated: 2026-09-25 23:55:47
-- ===============================================================

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;
CREATE TABLE claims (
	id INTEGER NOT NULL, 
	item_id INTEGER NOT NULL, 
	claimant_id INTEGER NOT NULL, 
	claim_reason TEXT NOT NULL, 
	private_detail TEXT NOT NULL, 
	supporting_information TEXT, 
	status VARCHAR(30) NOT NULL, 
	admin_comment TEXT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(item_id) REFERENCES items (id), 
	FOREIGN KEY(claimant_id) REFERENCES users (id)
);
INSERT INTO "claims" VALUES(1,9,4,'I lost this brown Titan wallet during the morning guest lecture in the main auditorium.','The wallet contains a Mumbai Metro smart card ending in digits 8812 and my Aadhaar photo.','Purchased from Titan World Bandra in Jan 2026. Contact via WhatsApp.','Approved','Identity verified against metro smart card records. Approved for collection at Admin Block Room 104.','2026-09-21 23:48:19.780309','2026-09-22 23:48:19.780309');
INSERT INTO "claims" VALUES(2,7,2,'Left my laptop on the desk while attending the 2:30 PM tutorial session in Library 2nd Floor.','Lock screen has a wallpaper of Chandrayaan-3, and username is ''aarav_sharma''.','Student ID CE-2023-015.','Pending',NULL,'2026-09-25 17:48:19.780309','2026-09-25 23:48:19.784770');
CREATE TABLE items (
	id INTEGER NOT NULL, 
	reporter_id INTEGER NOT NULL, 
	item_type VARCHAR(10) NOT NULL, 
	item_name VARCHAR(120) NOT NULL, 
	category VARCHAR(50) NOT NULL, 
	description TEXT NOT NULL, 
	brand VARCHAR(80), 
	color VARCHAR(50), 
	location VARCHAR(120) NOT NULL, 
	item_date DATE NOT NULL, 
	approximate_time VARCHAR(50), 
	identifying_marks TEXT, 
	estimated_value FLOAT, 
	image_filename VARCHAR(255), 
	status VARCHAR(30) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(reporter_id) REFERENCES users (id)
);
INSERT INTO "items" VALUES(1,2,'Lost','Dell Inspiron 15 Laptop','Laptop','Silver Dell Inspiron 15-inch laptop with Python and GitHub stickers on the top lid.','Dell','Silver','Central Library 2nd Floor','2026-09-23','2:30 PM','Small scratch near charging port, GitHub Octocat sticker',58000.0,'dell_inspiron_lost.jpg','Possible Match','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(2,3,'Lost','VSIT Student ID Card & Lanyard','ID Card','Blue VSIT (Vidyalankar School of Information Technology) RFID ID card inside a transparent badge holder with a blue college lanyard.','VSIT','Blue','Campus Canteen','2026-09-24','1:15 PM','Roll Number IT-2023-042 printed on front',250.0,'vsit_id_card_lost.jpg','Possible Match','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(3,4,'Lost','Wildcraft Black College Backpack','Bag','Wildcraft black 30L rucksack backpack containing engineering drawing instruments and notes.','Wildcraft','Black','Football Ground Pavilion','2026-09-22','5:00 PM','Reflective orange zipper pull on front pocket',2200.0,'wildcraft_backpack_lost.jpg','Open','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(4,2,'Lost','Apple AirPods Pro 2','Electronic Accessory','White Apple AirPods Pro wireless earbuds in MagSafe charging case with a transparent silicone case.','Apple','White','Computer Lab 3','2026-09-21','11:45 AM','Laser engraved ''A.S.'' on front of charging case',19500.0,'airpods_pro_lost.jpg','Open','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(5,4,'Lost','Brown Leather Titan Wallet','Wallet or Purse','Genuine brown leather bifold wallet with cash, metro smart card, and college library card.','Titan','Brown','Main Auditorium Hall','2026-09-20','4:15 PM','Embossed Titan crest on bottom-right corner',1400.0,'brown_wallet_lost.jpg','Claim Approved','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(6,3,'Lost','Engineering Mathematics Vol 3 Book','Books or Notes','Higher Engineering Mathematics reference textbook with yellow highlighter marks in Chapter 4.','Khanna Publishers','Blue and Yellow','Mechanical Workshop Block','2026-09-19','10:00 AM','Name ''Priya P.'' penned inside front cover',850.0,'math_book_lost.jpg','Returned','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(7,3,'Found','Silver Dell Laptop in Padded Sleeve','Laptop','Dell silver laptop found on an empty study desk in the reading room. Handed over to library circulation desk.','Dell','Silver','Central Library 2nd Floor','2026-09-23','3:15 PM','Lid has stickers; charging adapter was left alongside',55000.0,'dell_laptop_found.jpg','Possible Match','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(8,4,'Found','Student ID Card with Blue Lanyard','ID Card','VSIT (Vidyalankar School of Information Technology) student identity card found near the juice counter in the main canteen.','VSIT','Blue','Campus Canteen','2026-09-24','2:00 PM','Kept securely with canteen supervisor',200.0,'id_card_found.jpg','Possible Match','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(9,2,'Found','Titan Brown Men''s Leather Wallet','Wallet or Purse','Brown bi-fold wallet spotted on row 4 seat in the auditorium following the annual guest lecture.','Titan','Brown','Main Auditorium Hall','2026-09-20','5:30 PM','Contains transit card and notes',1200.0,'brown_wallet_found.jpg','Claim Approved','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(10,4,'Found','Casio FX-991CW Scientific Calculator','Electronic Accessory','Black and white scientific calculator found under a desk in Physics Lab 2.','Casio','Black','Physics Lab 2','2026-09-22','12:00 PM','Transparent tape over battery compartment',1250.0,'casio_calculator_found.jpg','Open','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(11,2,'Found','Set of 3 Yale Keys on Red Keychain','Keys','Three silver Yale metal keys attached to a red woven VSIT keychain strap.','Yale','Silver','VSIT IT Seminar Hall','2026-09-24','9:30 AM','One key has a green plastic tag',300.0,'keys_keychain_found.jpg','Open','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
INSERT INTO "items" VALUES(12,4,'Found','Higher Engineering Mathematics Textbook','Books or Notes','Textbook found on the wooden bench outside the mechanical workshop.','Khanna','Blue','Mechanical Workshop Block','2026-09-19','11:30 AM','Notes written in pencil',800.0,'math_book_found.jpg','Returned','2026-09-25 23:48:19.738149','2026-09-25 23:48:19.738149');
CREATE TABLE matches (
	id INTEGER NOT NULL, 
	lost_item_id INTEGER NOT NULL, 
	found_item_id INTEGER NOT NULL, 
	match_score INTEGER NOT NULL, 
	match_reason TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	is_seen BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_lost_found_match UNIQUE (lost_item_id, found_item_id), 
	FOREIGN KEY(lost_item_id) REFERENCES items (id), 
	FOREIGN KEY(found_item_id) REFERENCES items (id)
);
INSERT INTO "matches" VALUES(1,1,7,100,'Same category, Similar item name, Same brand, Same color, Same or nearby location, and similar description keywords.','2026-09-23 23:48:19.758256',1);
INSERT INTO "matches" VALUES(2,2,8,100,'Same category, Similar item name, Same brand, Same color, Same or nearby location, and similar description keywords.','2026-09-24 23:48:19.760520',1);
INSERT INTO "matches" VALUES(3,5,9,100,'Same category, Similar item name, Same brand, Same color, Same or nearby location, and similar description keywords.','2026-09-20 23:48:19.762530',1);
CREATE TABLE notifications (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	message TEXT NOT NULL, 
	notification_type VARCHAR(50) NOT NULL, 
	is_read BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO "notifications" VALUES(1,2,'Smart Match Alert (100% match): Found item ''Silver Dell Laptop in Padded Sleeve'' matches your lost report ''Dell Inspiron 15 Laptop''.','match_found',0,'2026-09-23 23:48:19.801558');
INSERT INTO "notifications" VALUES(2,3,'Smart Match Alert (100% match): Found item ''Student ID Card with Blue Lanyard'' matches your lost report ''VSIT Student ID Card & Lanyard''.','match_found',0,'2026-09-24 23:48:19.804865');
INSERT INTO "notifications" VALUES(3,4,'Your claim on item ''Titan Brown Men''s Leather Wallet'' has been APPROVED by the campus administration! Please visit Admin Block Room 104 with your student ID.','claim_approved',1,'2026-09-22 23:48:19.804865');
CREATE TABLE users (
	id INTEGER NOT NULL, 
	full_name VARCHAR(100) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	phone VARCHAR(20), 
	department VARCHAR(100), 
	created_at DATETIME NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "users" VALUES(1,'Dr. Sunita Kulkarni','admin@vsit.edu.in','scrypt:32768:8:1$SKelfoYogS1sZoTg$22f361107788ef60d27efd764cb6aace0ca2ba5761c40b36d3ecb96a76cfa2ad3eb82b0d96a9dc8225c1e859d2f2910f0453554f66d4eb7b54807cf87684e81d','admin','+91 22 2800 1200','Campus Operations & Student Welfare','2026-09-25 23:48:19.713814',1);
INSERT INTO "users" VALUES(2,'Aarav Sharma','aarav.sharma@vsit.edu.in','scrypt:32768:8:1$8ClRAvTGrFe1CkJT$ff55cc1e106244d849797a7ac1194a033a9f6c86f175cada280043375bec4d0cee9e5ec03442e2aab9166ba663991595ea7fc7ae11c5792cae22f73387ede3da','student','+91 98201 11223','B.Sc. Information Technology','2026-09-25 23:48:19.713814',1);
INSERT INTO "users" VALUES(3,'Priya Patel','priya.patel@vsit.edu.in','scrypt:32768:8:1$KcBR9R4ZKso4Axmp$fef7e522f66dedb343823ab3328ba61cc8612ac461f1337173539d646b489712555118668e750dc755702bedbdebf4f5307f17b5bfc43151f318acf8208d5eb4','student','+91 98202 33445','B.Sc. Computer Science','2026-09-25 23:48:19.713814',1);
INSERT INTO "users" VALUES(4,'Rohan Deshmukh','rohan.deshmukh@vsit.edu.in','scrypt:32768:8:1$ESMd7sStEnuhe6Km$4edd9233ba5a055684201d0767a2c5c463e434b649069ca4a4ed6d5cb51803c3ee2d3ba3fb8657946aa8c2c5e568cce4819b90daf30daa8bc44f77eeba79d313','student','+91 98203 55667','Bachelor of Management Studies (BMS)','2026-09-25 23:48:19.713814',1);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_items_item_type ON items (item_type);
CREATE INDEX ix_items_item_name ON items (item_name);
CREATE INDEX ix_items_reporter_id ON items (reporter_id);
CREATE INDEX ix_items_category ON items (category);
CREATE INDEX ix_items_status ON items (status);
CREATE INDEX ix_notifications_user_id ON notifications (user_id);
CREATE INDEX ix_matches_lost_item_id ON matches (lost_item_id);
CREATE INDEX ix_matches_found_item_id ON matches (found_item_id);
CREATE INDEX ix_claims_item_id ON claims (item_id);
CREATE INDEX ix_claims_status ON claims (status);
CREATE INDEX ix_claims_claimant_id ON claims (claimant_id);
COMMIT;