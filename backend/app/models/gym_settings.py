
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GymSettings(Base):
    __tablename__ = "gym_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    gym_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="My Gym",
    )

    slogan: Mapped[str | None] = mapped_column(String(255), nullable=True)
    upi_id: Mapped[str | None] = mapped_column(String(150), nullable=True)
    upi_qr_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hero_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    male_opening_hours: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    female_opening_hours: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
