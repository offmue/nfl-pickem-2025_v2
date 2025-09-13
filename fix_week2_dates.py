#!/usr/bin/env python3
"""
Korrigiere die Woche 2 Spielzeiten
"""

from app import app, db, Match, Team
from datetime import datetime
import pytz

def fix_week2_dates():
    with app.app_context():
        print("=== WOCHE 2 SPIELZEITEN KORRIGIEREN ===")
        
        # Wiener Zeitzone
        vienna_tz = pytz.timezone('Europe/Vienna')
        
        # Thursday Night Game: Packers @ Commanders
        packers = Team.query.filter_by(name='Green Bay Packers').first()
        commanders = Team.query.filter_by(name='Washington Commanders').first()
        
        thursday_game = Match.query.filter_by(
            week=2,
            away_team_id=packers.id,
            home_team_id=commanders.id
        ).first()
        
        if thursday_game:
            # Donnerstag, 12. September 2025, 20:15 Wiener Zeit (bereits gespielt)
            thursday_date = vienna_tz.localize(datetime(2025, 9, 12, 20, 15))
            thursday_game.start_time = thursday_date
            print(f"✅ Thursday Night: {packers.name} @ {commanders.name} → {thursday_date}")
        
        # Monday Night Game: Buccaneers @ Texans  
        buccaneers = Team.query.filter_by(name='Tampa Bay Buccaneers').first()
        texans = Team.query.filter_by(name='Houston Texans').first()
        
        monday_game = Match.query.filter_by(
            week=2,
            away_team_id=buccaneers.id,
            home_team_id=texans.id
        ).first()
        
        if monday_game:
            # Montag, 16. September 2025, 21:15 Wiener Zeit
            monday_date = vienna_tz.localize(datetime(2025, 9, 16, 21, 15))
            monday_game.start_time = monday_date
            print(f"✅ Monday Night: {buccaneers.name} @ {texans.name} → {monday_date}")
        
        # Alle anderen Spiele: Sonntag, 15. September 2025
        sunday_games = Match.query.filter_by(week=2).filter(
            Match.id != (thursday_game.id if thursday_game else 0),
            Match.id != (monday_game.id if monday_game else 0)
        ).all()
        
        for game in sunday_games:
            # Verschiedene Sonntag-Zeiten (19:00, 22:25)
            if game.id % 2 == 0:
                sunday_date = vienna_tz.localize(datetime(2025, 9, 15, 19, 0))  # 19:00
            else:
                sunday_date = vienna_tz.localize(datetime(2025, 9, 15, 22, 25))  # 22:25
            
            game.start_time = sunday_date
            away_team = Team.query.get(game.away_team_id)
            home_team = Team.query.get(game.home_team_id)
            print(f"✅ Sunday: {away_team.name} @ {home_team.name} → {sunday_date}")
        
        db.session.commit()
        print("\n✅ Woche 2 Spielzeiten erfolgreich korrigiert!")
        
        # Zeige aktuellen Status
        print("\n=== AKTUELLE WOCHE 2 SPIELE ===")
        all_week2_games = Match.query.filter_by(week=2).order_by(Match.start_time).all()
        
        for game in all_week2_games:
            away_team = Team.query.get(game.away_team_id)
            home_team = Team.query.get(game.home_team_id)
            local_time = game.start_time.strftime('%A, %d. %B %Y, %H:%M')
            status = "GESPIELT" if game.is_game_started else "KOMMEND"
            print(f"{away_team.name} @ {home_team.name} - {local_time} ({status})")

if __name__ == '__main__':
    fix_week2_dates()

