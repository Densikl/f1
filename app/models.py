import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Team(db.Model):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    base: Mapped[str]
    power_unit: Mapped[str]

    drivers: Mapped[list["Driver"]] = relationship(back_populates="team")

    def to_dict(self, include_drivers=False):
        data = {
            "id": self.id,
            "name": self.name,
            "base": self.base,
            "power_unit": self.power_unit,
        }
        if include_drivers:
            data["drivers"] = [driver.to_dict() for driver in self.drivers]
        return data


class Driver(db.Model):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    number: Mapped[int]
    nationality: Mapped[str]
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))

    team: Mapped[Team] = relationship(back_populates="drivers")
    results: Mapped[list["RaceResult"]] = relationship(back_populates="driver")

    def to_dict(self, include_team=False):
        data = {
            "id": self.id,
            "code": self.code,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "number": self.number,
            "nationality": self.nationality,
            "team_id": self.team_id,
        }
        if include_team:
            data["team"] = self.team.to_dict()
        return data


class Race(db.Model):
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True)
    round: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    circuit: Mapped[str]
    country: Mapped[str]
    date: Mapped[datetime.date]

    results: Mapped[list["RaceResult"]] = relationship(back_populates="race")

    def to_dict(self):
        return {
            "id": self.id,
            "round": self.round,
            "name": self.name,
            "circuit": self.circuit,
            "country": self.country,
            "date": self.date.isoformat(),
        }


class RaceResult(db.Model):
    __tablename__ = "race_results"
    __table_args__ = (UniqueConstraint("race_id", "driver_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    position: Mapped[int | None]
    points: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(default="Finished")

    race: Mapped[Race] = relationship(back_populates="results")
    driver: Mapped[Driver] = relationship(back_populates="results")

    def to_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "points": self.points,
            "status": self.status,
            "race": {"id": self.race.id, "round": self.race.round, "name": self.race.name},
            "driver": {
                "id": self.driver.id,
                "code": self.driver.code,
                "name": f"{self.driver.first_name} {self.driver.last_name}",
            },
        }
