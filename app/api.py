from flask import Blueprint, abort, jsonify, request

from .models import Driver, Race, RaceResult, Team, db

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/teams")
def list_teams():
    teams = db.session.scalars(db.select(Team).order_by(Team.id)).all()
    return jsonify([team.to_dict() for team in teams])


@api.get("/teams/<int:team_id>")
def get_team(team_id):
    team = db.get_or_404(Team, team_id, description="Team not found")
    return jsonify(team.to_dict(include_drivers=True))


@api.get("/drivers")
def list_drivers():
    query = db.select(Driver).order_by(Driver.id)

    team_id = request.args.get("team_id")
    if team_id is not None:
        if not team_id.isdigit():
            abort(400, description="team_id must be an integer")
        query = query.where(Driver.team_id == int(team_id))

    drivers = db.session.scalars(query).all()
    return jsonify([driver.to_dict() for driver in drivers])


@api.get("/drivers/<int:driver_id>")
def get_driver(driver_id):
    driver = db.get_or_404(Driver, driver_id, description="Driver not found")
    return jsonify(driver.to_dict(include_team=True))


@api.get("/drivers/<int:driver_id>/results")
def get_driver_results(driver_id):
    driver = db.get_or_404(Driver, driver_id, description="Driver not found")
    query = (
        db.select(RaceResult)
        .join(RaceResult.race)
        .where(RaceResult.driver_id == driver.id)
        .order_by(Race.round)
    )
    results = db.session.scalars(query).all()
    return jsonify([result.to_dict() for result in results])


@api.get("/races")
def list_races():
    races = db.session.scalars(db.select(Race).order_by(Race.round)).all()
    return jsonify([race.to_dict() for race in races])


@api.get("/races/<int:race_id>")
def get_race(race_id):
    race = db.get_or_404(Race, race_id, description="Race not found")
    return jsonify(race.to_dict())


@api.get("/races/<int:race_id>/results")
def get_race_results(race_id):
    race = db.get_or_404(Race, race_id, description="Race not found")
    query = (
        db.select(RaceResult)
        .where(RaceResult.race_id == race.id)
        .order_by(RaceResult.position.asc().nulls_last())
    )
    results = db.session.scalars(query).all()
    return jsonify([result.to_dict() for result in results])
