
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Attendance, Member, Plan, Subscription, User, Workout
from app.api.auth import get_current_user
from app.schemas.member_portal import MemberProfileUpdate


router = APIRouter(
    prefix="/member-portal",
    tags=["Member Portal"],
)


def get_linked_member(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Member:
    if current_user.role != "member":
        raise HTTPException(
            status_code=403,
            detail="Member account required",
        )

    if current_user.member_id is None:
        raise HTTPException(
            status_code=403,
            detail="Your account is not linked to a gym member profile",
        )

    member = db.get(Member, current_user.member_id)

    if member is None:
        raise HTTPException(
            status_code=404,
            detail="Linked gym member profile not found",
        )

    return member


def calculate_bmi(member: Member) -> float | None:
    if (
        member.height_cm is None
        or member.weight_kg is None
        or member.height_cm <= 0
        or member.weight_kg <= 0
    ):
        return None

    height_m = member.height_cm / 100
    return round(member.weight_kg / (height_m ** 2), 2)


@router.get("/profile")
def get_profile(
    member: Member = Depends(get_linked_member),
):
    return {
        "id": member.id,
        "name": member.name,
        "age": member.age,
        "phone": member.phone,
        "photo_path": member.photo_path,
        "height_cm": member.height_cm,
        "weight_kg": member.weight_kg,
        "bmi": calculate_bmi(member),
    }


@router.put("/profile")
def update_profile(
    data: MemberProfileUpdate,
    member: Member = Depends(get_linked_member),
    db: Session = Depends(get_db),
):
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        return {
            "message": "No changes supplied",
            "member_id": member.id,
        }

    for field in ("name", "age", "phone"):
        if field in changes and changes[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

    for field, value in changes.items():
        setattr(member, field, value)

    try:
        db.commit()
        db.refresh(member)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="The phone number may already belong to another member",
        )

    return {
        "message": "Profile updated successfully",
        "id": member.id,
        "name": member.name,
        "age": member.age,
        "phone": member.phone,
        "photo_path": member.photo_path,
        "height_cm": member.height_cm,
        "weight_kg": member.weight_kg,
        "bmi": calculate_bmi(member),
    }


@router.get("/subscription")
def get_my_subscription(
    member: Member = Depends(get_linked_member),
    db: Session = Depends(get_db),
):
    result = (
        db.query(Subscription, Plan)
        .join(Plan, Subscription.plan_id == Plan.id)
        .filter(Subscription.member_id == member.id)
        .order_by(
            Subscription.start_date.desc(),
            Subscription.id.desc(),
        )
        .first()
    )

    if result is None:
        return {
            "subscription": None,
            "message": "No subscription found",
        }

    subscription, plan = result
    today = date.today()
    display_status = subscription.status

    if subscription.end_date < today:
        display_status = "expired"
    elif subscription.start_date > today and display_status == "active":
        display_status = "upcoming"

    return {
        "subscription_id": subscription.id,
        "member_id": member.id,
        "plan_id": plan.id,
        "plan_name": plan.name,
        "plan_price": float(plan.price),
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "status": display_status,
        "days_remaining": max(
            (subscription.end_date - today).days,
            0,
        ),
    }


@router.get("/attendance")
def get_my_attendance(
    member: Member = Depends(get_linked_member),
    db: Session = Depends(get_db),
):
    records = (
        db.query(Attendance)
        .filter(Attendance.member_id == member.id)
        .order_by(
            Attendance.attendance_date.desc(),
            Attendance.id.desc(),
        )
        .all()
    )

    return [
        {
            "id": record.id,
            "attendance_date": record.attendance_date,
            "check_in_time": record.check_in_time,
            "workout_focus": record.workout_focus,
            "status": record.status,
        }
        for record in records
    ]


@router.get("/workouts")
def get_my_workouts(
    member: Member = Depends(get_linked_member),
    db: Session = Depends(get_db),
):
    records = (
        db.query(Workout)
        .filter(Workout.member_id == member.id)
        .order_by(
            Workout.workout_date.desc(),
            Workout.id.desc(),
        )
        .all()
    )

    return [
        {
            "id": record.id,
            "workout_date": record.workout_date,
            "body_part": record.body_part,
            "notes": record.notes,
        }
        for record in records
    ]
