from getpass import getpass

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import User
from app.core.security import hash_password


def main():
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password (min 12 characters): ")
    confirm_password = getpass("Confirm password: ")

    if not name or not email:
        print("Name and email are required.")
        return

    if len(password) < 12:
        print("Password must be at least 12 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    db: Session = SessionLocal()

    try:
        existing = db.query(User).filter(User.email == email).first()

        if existing:
            print("This email already exists. No changes made.")
            return

        admin = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print(f"Admin account created: {email}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()