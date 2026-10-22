import datetime
import json
from pathlib import Path

from .models import Driver, Race, RaceResult, Team, db

SNAPSHOT = Path(__file__).parent / "data" / "season_2026.json"


def seed():
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    db.drop_all()
    db.create_all()

    teams = {}
    for team in data["teams"]:
        teams[team["name"]] = Team(name=team["name"], base=team["base"], power_unit=team["power_unit"])
    db.session.add_all(teams.values())

    drivers = {}
    for driver in data["drivers"]:
        drivers[driver["code"]] = Driver(
            code=driver["code"],
            first_name=driver["first_name"],
            last_name=driver["last_name"],
            number=driver["number"],
            nationality=driver["nationality"],
            team=teams.get(driver["team"]),
        )
    db.session.add_all(drivers.values())

    for race_data in data["races"]:
        race = Race(
            round=race_data["round"],
            name=race_data["name"],
            circuit=race_data["circuit"],
            country=race_data["country"],
            date=datetime.date.fromisoformat(race_data["date"]),
        )
        db.session.add(race)

        for result in race_data["results"]:
            db.session.add(
                RaceResult(
                    race=race,
                    driver=drivers[result["driver"]],
                    team=teams[result["team"]],
                    position=result["position"],
                    points=result["points"],
                    status=result["status"],
                )
            )

    db.session.commit()
