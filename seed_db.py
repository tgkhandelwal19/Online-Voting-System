import random
from app import app
from models import db, User, Candidate, Vote
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def seed_database():
    with app.app_context():
        # Prevent duplicate seeding
        if Candidate.query.count() > 0:
            print("Database already contains candidates. Seeding aborted to prevent duplicates.")
            print("If you want to re-seed, use the 'Reset Entire Election' option from the Admin Dashboard first.")
            return

        print("Starting to seed database with sample data...")

        # 1. Create 5 Candidates
        candidates_data = [
            {"name": "Narendra Modi", "party": "Bharatiya Janata Party", "agenda": "Cultural nationalism (Hindutva), economic development, and governance reforms."},
            {"name": "Rahul Gandhi", "party": "Indian National Congress", "agenda": "Defending the Indian Constitution, fighting institutional capture, and promoting social equality."},
            {"name": "Arvind Kejriwal", "party": "Aam Aadmi Party", "agenda": "Fighting corruption, delivering honest governance, and providing accessible public welfare."},
            {"name": "Mamta Banerjee", "party": "All India Trinamool Congress", "agenda": "Grassroots empowerment, secularism, and social justice."},
            {"name": "C. Joseph Vijay", "party": "Tamilaga Vettri Kazhagam", "agenda": "Secularism, social justice, egalitarianism, and a corruption-free administration."}
        ]
        
        db_candidates = []
        for data in candidates_data:
            candidate = Candidate(name=data["name"], party=data["party"], agenda=data["agenda"])
            db.session.add(candidate)
            db_candidates.append(candidate)
            
        # Commit candidates first so they get valid IDs to link votes to
        db.session.commit()
        print(f"✅ Inserted {len(db_candidates)} candidates.")

        # 2. Create 10 Voters
        # Using a shared password hash is faster than hashing 10 separate times per script execution
        default_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        db_users = []
        
        for i in range(1, 11):
            user = User(
                voter_id=f"VOTER{i:03d}",  # e.g., VOTER001, VOTER002
                name=f"Demo User {i}",
                role="user",
                password_hash=default_password,
                has_voted=False
            )
            db.session.add(user)
            db_users.append(user)

        # Commit users so they get valid IDs
        db.session.commit()
        print(f"✅ Inserted {len(db_users)} users (Voter IDs: VOTER001 to VOTER010).")

        # 3. Simulate Realistic Votes
        # Pick 7 random users who will cast their votes
        users_who_voted = random.sample(db_users, 7)
        
        for user in users_who_voted:
            # Randomly pick a candidate for this user to vote for
            chosen_candidate = random.choice(db_candidates)
            
            # Create the Vote relation
            new_vote = Vote(voter_id=user.id, candidate_id=chosen_candidate.id)
            db.session.add(new_vote)
            
            # Lock the user's vote status
            user.has_voted = True
            
        db.session.commit()
        print(f"✅ Simulated strict voting process for {len(users_who_voted)} random users.")
        
        print("\n🎉 Seeding Complete! ")
        print("Test Credentials you can use now:")
        print("--------------------------------")
        print("Voter Login:  VOTER001  (Password: password123)")
        print("Admin Login:  admin     (Password: admin123)")

if __name__ == '__main__':
    seed_database()
