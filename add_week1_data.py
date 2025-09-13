#!/usr/bin/env python3
"""
Skript zum Hinzufügen der Woche 1 Daten und Ergebnisse
"""

from app import app, db, User, Team, Match, Pick, EliminatedTeam, TeamLoserUsage
from datetime import datetime
import pytz

def add_week1_data():
    with app.app_context():
        print("=== WOCHE 1 DATEN ERSETZEN ===")
        
        # Lösche bestehende Woche 1 Daten
        existing_picks = Pick.query.join(Match).filter(Match.week == 1).all()
        for pick in existing_picks:
            db.session.delete(pick)
        
        existing_matches = Match.query.filter_by(week=1).all()
        for match in existing_matches:
            db.session.delete(match)
        
        db.session.commit()
        print("✅ Bestehende Woche 1 Daten gelöscht")
        
        # Hole Teams
        falcons = Team.query.filter_by(name="Atlanta Falcons").first()
        buccaneers = Team.query.filter_by(name="Tampa Bay Buccaneers").first()
        broncos = Team.query.filter_by(name="Denver Broncos").first()
        titans = Team.query.filter_by(name="Tennessee Titans").first()
        bengals = Team.query.filter_by(name="Cincinnati Bengals").first()
        browns = Team.query.filter_by(name="Cleveland Browns").first()
        commanders = Team.query.filter_by(name="Washington Commanders").first()
        giants = Team.query.filter_by(name="New York Giants").first()
        
        # Hole Benutzer
        manuel = User.query.filter_by(username="Manuel").first()
        daniel = User.query.filter_by(username="Daniel").first()
        raff = User.query.filter_by(username="Raff").first()
        haunschi = User.query.filter_by(username="Haunschi").first()
        
        # Erstelle Woche 1 Spiele mit korrekten Ergebnissen
        vienna_tz = pytz.timezone('Europe/Vienna')
        week1_date = vienna_tz.localize(datetime(2025, 9, 8, 19, 0))  # Beispiel-Datum
        
        # Spiel 1: Falcons @ Buccaneers (Buccaneers gewonnen)
        match1 = Match(
            week=1,
            away_team_id=falcons.id,
            home_team_id=buccaneers.id,
            start_time=week1_date,
            is_completed=True,
            winner_team_id=buccaneers.id
        )
        db.session.add(match1)
        
        # Spiel 2: Broncos @ Titans (Broncos gewonnen)  
        match2 = Match(
            week=1,
            away_team_id=broncos.id,
            home_team_id=titans.id,
            start_time=week1_date,
            is_completed=True,
            winner_team_id=broncos.id
        )
        db.session.add(match2)
        
        # Spiel 3: Bengals @ Browns (Bengals gewonnen)
        match3 = Match(
            week=1,
            away_team_id=bengals.id,
            home_team_id=browns.id,
            start_time=week1_date,
            is_completed=True,
            winner_team_id=bengals.id
        )
        db.session.add(match3)
        
        # Spiel 4: Commanders @ Giants (Commanders gewonnen)
        match4 = Match(
            week=1,
            away_team_id=commanders.id,
            home_team_id=giants.id,
            start_time=week1_date,
            is_completed=True,
            winner_team_id=commanders.id
        )
        db.session.add(match4)
        
        # Commit Spiele
        db.session.commit()
        
        # Erstelle Picks
        # Manuel: Falcons (falsch)
        pick1 = Pick(
            user_id=manuel.id,
            match_id=match1.id,
            chosen_team_id=falcons.id
        )
        db.session.add(pick1)
        
        # Daniel: Broncos (richtig)
        pick2 = Pick(
            user_id=daniel.id,
            match_id=match2.id,
            chosen_team_id=broncos.id
        )
        db.session.add(pick2)
        
        # Raff: Bengals (richtig)
        pick3 = Pick(
            user_id=raff.id,
            match_id=match3.id,
            chosen_team_id=bengals.id
        )
        db.session.add(pick3)
        
        # Haunschi: Commanders (richtig)
        pick4 = Pick(
            user_id=haunschi.id,
            match_id=match4.id,
            chosen_team_id=commanders.id
        )
        db.session.add(pick4)
        
        # Commit alles
        db.session.commit()
        
        # Erstelle TeamLoserUsage und EliminatedTeam Einträge
        print("✅ Erstelle Verlierer-Verwendungen und Eliminierungen...")
        
        # Manuel: Falcons gewählt, Buccaneers verloren → Buccaneers eliminiert
        manuel_loser = TeamLoserUsage(user_id=manuel.id, team_id=buccaneers.id, week=1, match_id=match1.id)
        db.session.add(manuel_loser)
        manuel_elim = EliminatedTeam(user_id=manuel.id, team_id=buccaneers.id)
        db.session.add(manuel_elim)
        
        # Daniel: Broncos gewählt, Titans verloren → Titans eliminiert  
        daniel_loser = TeamLoserUsage(user_id=daniel.id, team_id=titans.id, week=1, match_id=match2.id)
        db.session.add(daniel_loser)
        daniel_elim = EliminatedTeam(user_id=daniel.id, team_id=titans.id)
        db.session.add(daniel_elim)
        
        # Raff: Bengals gewählt, Browns verloren → Browns eliminiert
        raff_loser = TeamLoserUsage(user_id=raff.id, team_id=browns.id, week=1, match_id=match3.id)
        db.session.add(raff_loser)
        raff_elim = EliminatedTeam(user_id=raff.id, team_id=browns.id)
        db.session.add(raff_elim)
        
        # Haunschi: Commanders gewählt, Giants verloren → Giants eliminiert
        haunschi_loser = TeamLoserUsage(user_id=haunschi.id, team_id=giants.id, week=1, match_id=match4.id)
        db.session.add(haunschi_loser)
        haunschi_elim = EliminatedTeam(user_id=haunschi.id, team_id=giants.id)
        db.session.add(haunschi_elim)
        db.session.commit()
        
        print("✅ Woche 1 Spiele erstellt:")
        print(f"  - Falcons @ Buccaneers (Gewinner: Buccaneers)")
        print(f"  - Broncos @ Titans (Gewinner: Broncos)")
        print(f"  - Bengals @ Browns (Gewinner: Bengals)")
        print(f"  - Commanders @ Giants (Gewinner: Commanders)")
        
        print("✅ Picks erstellt:")
        print(f"  - Manuel: Falcons (FALSCH) - 0 Punkte")
        print(f"  - Daniel: Broncos (RICHTIG) - 1 Punkt")
        print(f"  - Raff: Bengals (RICHTIG) - 1 Punkt")
        print(f"  - Haunschi: Commanders (RICHTIG) - 1 Punkt")
        
        print("✅ Eliminierte Teams:")
        print(f"  - Buccaneers (Manuel's Verlierer)")
        print(f"  - Titans (Daniel's Verlierer)")
        print(f"  - Browns (Raff's Verlierer)")
        print(f"  - Giants (Haunschi's Verlierer)")

if __name__ == "__main__":
    add_week1_data()

