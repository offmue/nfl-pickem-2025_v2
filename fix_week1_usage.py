#!/usr/bin/env python3
"""
Korrigiere die fehlenden TeamWinnerUsage Einträge für Woche 1
"""

from app import app, db, Pick, TeamWinnerUsage, Team, User

def fix_week1_usage():
    with app.app_context():
        print("=== WOCHE 1 TEAM WINNER USAGE KORRIGIEREN ===")
        
        # Hole alle Woche 1 Picks
        week1_picks = Pick.query.join(Pick.match).filter_by(week=1).all()
        
        print(f"Gefundene Woche 1 Picks: {len(week1_picks)}")
        
        for pick in week1_picks:
            user = User.query.get(pick.user_id)
            team = Team.query.get(pick.chosen_team_id)
            
            print(f"Verarbeite Pick: {user.username} → {team.name}")
            
            # Prüfe ob TeamWinnerUsage bereits existiert
            existing_usage = TeamWinnerUsage.query.filter_by(
                user_id=pick.user_id,
                team_id=pick.chosen_team_id
            ).first()
            
            if existing_usage:
                print(f"  → Usage bereits vorhanden: {existing_usage.usage_count}x")
            else:
                # Erstelle neuen TeamWinnerUsage Eintrag
                new_usage = TeamWinnerUsage(
                    user_id=pick.user_id,
                    team_id=pick.chosen_team_id,
                    usage_count=1
                )
                db.session.add(new_usage)
                print(f"  → Neuer Usage erstellt: 1x")
        
        db.session.commit()
        print("\n✅ TeamWinnerUsage für Woche 1 erfolgreich korrigiert!")
        
        # Zeige aktuellen Status
        print("\n=== AKTUELLE TEAM WINNER USAGE ===")
        all_usages = TeamWinnerUsage.query.all()
        
        for usage in all_usages:
            user = User.query.get(usage.user_id)
            team = Team.query.get(usage.team_id)
            print(f"{user.username}: {team.name} → {usage.usage_count}x")

if __name__ == '__main__':
    fix_week1_usage()

