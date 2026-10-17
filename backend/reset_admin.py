
from getpass import getpass

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def main():
    print("\n=== Gym SaaS Admin Reset ===")

    new_email = input("New admin email: ").strip().lower()
    new_name = input("Admin name: ").strip()

    if not new_email or not new_name or "@" not in new_email:
        print("Invalid name or email.")
        return

    password = getpass("New password (minimum 12 characters): ")
    confirm = getpass("Confirm new password: ")

    if len(password) < 12:
        print("Password must be at least 12 characters.")
        return

    if password != confirm:
        print("Passwords do not match.")
        return

    db = SessionLocal()

    try:
        users = db.scalars(
            select(User).where(User.role == "admin")
        ).all()

        existing_email_user = db.scalar(
            select(User).where(User.email == new_email)
        )

        if existing_email_user and existing_email_user not in users:
            print("That email already belongs to another account.")
            return

        if users:
            admin = users[0]
            admin.email = new_email
            admin.name = new_name
            admin.hashed_password = hash_password(password)
            admin.role = "admin"
            admin.is_active = True

            print(f"Updating existing admin account (ID {admin.id}).")
        else:
            admin = User(
                name=new_name,
                email=new_email,
                hashed_password=hash_password(password),
                role="admin",
                is_active=True,
                member_id=None,
            )
            db.add(admin)
            print("No admin found; creating the first admin account.")

        db.commit()

        print("\nAdmin account reset successfully.")
        print(f"Email: {new_email}")
        print("Password: the new password you entered")

    except Exception:
        db.rollback()
        print("Reset failed. Database changes were rolled back.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
