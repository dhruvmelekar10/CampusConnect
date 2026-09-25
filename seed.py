import os
from datetime import datetime, date, timedelta
from app import create_app
from models import db, User, Item, Match, Claim, Notification
from services.matching_service import calculate_match_score

app = create_app()

def seed_database():
    """Populates the database with realistic demo data for VSIT (Vidyalankar School of Information Technology)."""
    with app.app_context():
        print("Resetting database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding campus users...")
        # 1. Administrator
        admin = User(
            full_name="Dr. Sunita Kulkarni",
            email="admin@vsit.edu.in",
            role="admin",
            department="Campus Operations & Student Welfare",
            phone="+91 22 2800 1200",
            is_active=True
        )
        admin.set_password("Admin@123")

        # 2. Student 1: Aarav Sharma
        student1 = User(
            full_name="Aarav Sharma",
            email="aarav.sharma@vsit.edu.in",
            role="student",
            department="B.Sc. Information Technology",
            phone="+91 98201 11223",
            is_active=True
        )
        student1.set_password("Student@123")

        # 3. Student 2: Priya Patel
        student2 = User(
            full_name="Priya Patel",
            email="priya.patel@vsit.edu.in",
            role="student",
            department="B.Sc. Computer Science",
            phone="+91 98202 33445",
            is_active=True
        )
        student2.set_password("Student@123")

        # 4. Student 3: Rohan Deshmukh
        student3 = User(
            full_name="Rohan Deshmukh",
            email="rohan.deshmukh@vsit.edu.in",
            role="student",
            department="Bachelor of Management Studies (BMS)",
            phone="+91 98203 55667",
            is_active=True
        )
        student3.set_password("Student@123")

        db.session.add_all([admin, student1, student2, student3])
        db.session.commit()
        print("Users successfully seeded.")

        today = date.today()

        print("Seeding Lost & Found items...")
        # -----------------------------
        # Lost Items (Reported by users)
        # -----------------------------
        lost1 = Item(
            reporter_id=student1.id,
            item_type="Lost",
            item_name="Dell Inspiron 15 Laptop",
            category="Laptop",
            description="Silver Dell Inspiron 15-inch laptop with Python and GitHub stickers on the top lid.",
            brand="Dell",
            color="Silver",
            location="Central Library 2nd Floor",
            item_date=today - timedelta(days=2),
            approximate_time="2:30 PM",
            identifying_marks="Small scratch near charging port, GitHub Octocat sticker",
            estimated_value=58000.0,
            image_filename="dell_inspiron_lost.jpg",
            status="Possible Match"
        )

        lost2 = Item(
            reporter_id=student2.id,
            item_type="Lost",
            item_name="VSIT Student ID Card & Lanyard",
            category="ID Card",
            description="Blue VSIT (Vidyalankar School of Information Technology) RFID ID card inside a transparent badge holder with a blue college lanyard.",
            brand="VSIT",
            color="Blue",
            location="Campus Canteen",
            item_date=today - timedelta(days=1),
            approximate_time="1:15 PM",
            identifying_marks="Roll Number IT-2023-042 printed on front",
            estimated_value=250.0,
            image_filename="vsit_id_card_lost.jpg",
            status="Possible Match"
        )

        lost3 = Item(
            reporter_id=student3.id,
            item_type="Lost",
            item_name="Wildcraft Black College Backpack",
            category="Bag",
            description="Wildcraft black 30L rucksack backpack containing engineering drawing instruments and notes.",
            brand="Wildcraft",
            color="Black",
            location="Football Ground Pavilion",
            item_date=today - timedelta(days=3),
            approximate_time="5:00 PM",
            identifying_marks="Reflective orange zipper pull on front pocket",
            estimated_value=2200.0,
            image_filename="wildcraft_backpack_lost.jpg",
            status="Open"
        )

        lost4 = Item(
            reporter_id=student1.id,
            item_type="Lost",
            item_name="Apple AirPods Pro 2",
            category="Electronic Accessory",
            description="White Apple AirPods Pro wireless earbuds in MagSafe charging case with a transparent silicone case.",
            brand="Apple",
            color="White",
            location="Computer Lab 3",
            item_date=today - timedelta(days=4),
            approximate_time="11:45 AM",
            identifying_marks="Laser engraved 'A.S.' on front of charging case",
            estimated_value=19500.0,
            image_filename="airpods_pro_lost.jpg",
            status="Open"
        )

        lost5 = Item(
            reporter_id=student3.id,
            item_type="Lost",
            item_name="Brown Leather Titan Wallet",
            category="Wallet or Purse",
            description="Genuine brown leather bifold wallet with cash, metro smart card, and college library card.",
            brand="Titan",
            color="Brown",
            location="Main Auditorium Hall",
            item_date=today - timedelta(days=5),
            approximate_time="4:15 PM",
            identifying_marks="Embossed Titan crest on bottom-right corner",
            estimated_value=1400.0,
            image_filename="brown_wallet_lost.jpg",
            status="Claim Approved"
        )

        lost6 = Item(
            reporter_id=student2.id,
            item_type="Lost",
            item_name="Engineering Mathematics Vol 3 Book",
            category="Books or Notes",
            description="Higher Engineering Mathematics reference textbook with yellow highlighter marks in Chapter 4.",
            brand="Khanna Publishers",
            color="Blue and Yellow",
            location="Mechanical Workshop Block",
            item_date=today - timedelta(days=6),
            approximate_time="10:00 AM",
            identifying_marks="Name 'Priya P.' penned inside front cover",
            estimated_value=850.0,
            image_filename="math_book_lost.jpg",
            status="Returned"
        )

        # -----------------------------
        # Found Items (Reported by campus members)
        # -----------------------------
        found1 = Item(
            reporter_id=student2.id,
            item_type="Found",
            item_name="Silver Dell Laptop in Padded Sleeve",
            category="Laptop",
            description="Dell silver laptop found on an empty study desk in the reading room. Handed over to library circulation desk.",
            brand="Dell",
            color="Silver",
            location="Central Library 2nd Floor",
            item_date=today - timedelta(days=2),
            approximate_time="3:15 PM",
            identifying_marks="Lid has stickers; charging adapter was left alongside",
            estimated_value=55000.0,
            image_filename="dell_laptop_found.jpg",
            status="Possible Match"
        )

        found2 = Item(
            reporter_id=student3.id,
            item_type="Found",
            item_name="Student ID Card with Blue Lanyard",
            category="ID Card",
            description="VSIT (Vidyalankar School of Information Technology) student identity card found near the juice counter in the main canteen.",
            brand="VSIT",
            color="Blue",
            location="Campus Canteen",
            item_date=today - timedelta(days=1),
            approximate_time="2:00 PM",
            identifying_marks="Kept securely with canteen supervisor",
            estimated_value=200.0,
            image_filename="id_card_found.jpg",
            status="Possible Match"
        )

        found3 = Item(
            reporter_id=student1.id,
            item_type="Found",
            item_name="Titan Brown Men's Leather Wallet",
            category="Wallet or Purse",
            description="Brown bi-fold wallet spotted on row 4 seat in the auditorium following the annual guest lecture.",
            brand="Titan",
            color="Brown",
            location="Main Auditorium Hall",
            item_date=today - timedelta(days=5),
            approximate_time="5:30 PM",
            identifying_marks="Contains transit card and notes",
            estimated_value=1200.0,
            image_filename="brown_wallet_found.jpg",
            status="Claim Approved"
        )

        found4 = Item(
            reporter_id=student3.id,
            item_type="Found",
            item_name="Casio FX-991CW Scientific Calculator",
            category="Electronic Accessory",
            description="Black and white scientific calculator found under a desk in Physics Lab 2.",
            brand="Casio",
            color="Black",
            location="Physics Lab 2",
            item_date=today - timedelta(days=3),
            approximate_time="12:00 PM",
            identifying_marks="Transparent tape over battery compartment",
            estimated_value=1250.0,
            image_filename="casio_calculator_found.jpg",
            status="Open"
        )

        found5 = Item(
            reporter_id=student1.id,
            item_type="Found",
            item_name="Set of 3 Yale Keys on Red Keychain",
            category="Keys",
            description="Three silver Yale metal keys attached to a red woven VSIT keychain strap.",
            brand="Yale",
            color="Silver",
            location="VSIT IT Seminar Hall",
            item_date=today - timedelta(days=1),
            approximate_time="9:30 AM",
            identifying_marks="One key has a green plastic tag",
            estimated_value=300.0,
            image_filename="keys_keychain_found.jpg",
            status="Open"
        )

        found6 = Item(
            reporter_id=student3.id,
            item_type="Found",
            item_name="Higher Engineering Mathematics Textbook",
            category="Books or Notes",
            description="Textbook found on the wooden bench outside the mechanical workshop.",
            brand="Khanna",
            color="Blue",
            location="Mechanical Workshop Block",
            item_date=today - timedelta(days=6),
            approximate_time="11:30 AM",
            identifying_marks="Notes written in pencil",
            estimated_value=800.0,
            image_filename="math_book_found.jpg",
            status="Returned"
        )

        db.session.add_all([lost1, lost2, lost3, lost4, lost5, lost6, found1, found2, found3, found4, found5, found6])
        db.session.commit()
        print("Items successfully seeded.")

        print("Computing and seeding Smart Matches...")
        # Smart Match 1: Lost Dell Inspiron (lost1) <=> Found Dell Laptop (found1)
        score1, _, reason1 = calculate_match_score(lost1, found1)
        match1 = Match(
            lost_item_id=lost1.id,
            found_item_id=found1.id,
            match_score=score1,
            match_reason=reason1,
            created_at=datetime.now() - timedelta(days=2),
            is_seen=True
        )

        # Smart Match 2: Lost Student ID (lost2) <=> Found Student ID (found2)
        score2, _, reason2 = calculate_match_score(lost2, found2)
        match2 = Match(
            lost_item_id=lost2.id,
            found_item_id=found2.id,
            match_score=score2,
            match_reason=reason2,
            created_at=datetime.now() - timedelta(days=1),
            is_seen=True
        )

        # Smart Match 3: Lost Titan Wallet (lost5) <=> Found Titan Wallet (found3)
        score3, _, reason3 = calculate_match_score(lost5, found3)
        match3 = Match(
            lost_item_id=lost5.id,
            found_item_id=found3.id,
            match_score=score3,
            match_reason=reason3,
            created_at=datetime.now() - timedelta(days=5),
            is_seen=True
        )

        db.session.add_all([match1, match2, match3])
        db.session.commit()
        print(f"Match 1 created with score: {score1}% ({reason1})")
        print(f"Match 2 created with score: {score2}% ({reason2})")
        print(f"Match 3 created with score: {score3}% ({reason3})")

        print("Seeding sample Claims...")
        # 1. Approved Claim by Rohan on the Titan Wallet (found3)
        claim1 = Claim(
            item_id=found3.id,
            claimant_id=student3.id,
            claim_reason="I lost this brown Titan wallet during the morning guest lecture in the main auditorium.",
            private_detail="The wallet contains a Mumbai Metro smart card ending in digits 8812 and my Aadhaar photo.",
            supporting_information="Purchased from Titan World Bandra in Jan 2026. Contact via WhatsApp.",
            status="Approved",
            admin_comment="Identity verified against metro smart card records. Approved for collection at Admin Block Room 104.",
            created_at=datetime.now() - timedelta(days=4),
            updated_at=datetime.now() - timedelta(days=3)
        )

        # 2. Pending Claim by Aarav on Dell Laptop (found1)
        claim2 = Claim(
            item_id=found1.id,
            claimant_id=student1.id,
            claim_reason="Left my laptop on the desk while attending the 2:30 PM tutorial session in Library 2nd Floor.",
            private_detail="Lock screen has a wallpaper of Chandrayaan-3, and username is 'aarav_sharma'.",
            supporting_information="Student ID CE-2023-015.",
            status="Pending",
            admin_comment=None,
            created_at=datetime.now() - timedelta(hours=6)
        )

        db.session.add_all([claim1, claim2])
        db.session.commit()

        print("Seeding in-app Notifications...")
        n1 = Notification(
            user_id=student1.id,
            message=f"Smart Match Alert ({score1}% match): Found item '{found1.item_name}' matches your lost report '{lost1.item_name}'.",
            notification_type="match_found",
            is_read=False,
            created_at=datetime.now() - timedelta(days=2)
        )

        n2 = Notification(
            user_id=student2.id,
            message=f"Smart Match Alert ({score2}% match): Found item '{found2.item_name}' matches your lost report '{lost2.item_name}'.",
            notification_type="match_found",
            is_read=False,
            created_at=datetime.now() - timedelta(days=1)
        )

        n3 = Notification(
            user_id=student3.id,
            message="Your claim on item 'Titan Brown Men's Leather Wallet' has been APPROVED by the campus administration! Please visit Admin Block Room 104 with your student ID.",
            notification_type="claim_approved",
            is_read=True,
            created_at=datetime.now() - timedelta(days=3)
        )

        db.session.add_all([n1, n2, n3])
        db.session.commit()

        print("\n=======================================================")
        print("CampusConnect Demo Database successfully seeded!")
        print("VSIT (Vidyalankar School of Information Technology) Portal Credentials:")
        print("-------------------------------------------------------")
        print("1. Administrator:")
        print("   Email:    admin@vsit.edu.in")
        print("   Password: Admin@123")
        print("2. Student (Aarav Sharma - B.Sc. IT):")
        print("   Email:    aarav.sharma@vsit.edu.in")
        print("   Password: Student@123")
        print("3. Student (Priya Patel - B.Sc. CS):")
        print("   Email:    priya.patel@vsit.edu.in")
        print("   Password: Student@123")
        print("4. Student (Rohan Deshmukh - BMS):")
        print("   Email:    rohan.deshmukh@vsit.edu.in")
        print("   Password: Student@123")
        print("=======================================================\n")

if __name__ == '__main__':
    seed_database()
