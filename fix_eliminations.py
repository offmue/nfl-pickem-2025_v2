#!/usr/bin/env python3
"""
Fix missing eliminations for existing picks
"""

from app import app, db, User, Team, Match, Pick, EliminatedTeam, TeamLoserUsage

def fix_eliminations():
    with app.app_context():
        print("=== ELIMINIERUNGEN KORRIGIEREN ===")
        
        # Lösche alle bestehenden Eliminierungen (für sauberen Neustart)
        EliminatedTeam.query.delete()
        db.session.commit()
        print("✅ Bestehende Eliminierungen gelöscht")
        
        # Hole alle TeamLoserUsage Einträge
        loser_usages = TeamLoserUsage.query.all()
        
        print(f"📊 Gefunden: {len(loser_usages)} Verlierer-Verwendungen")
        
        # Erstelle Eliminierungen für alle Teams, die als Verlierer verwendet wurden
        for loser_usage in loser_usages:
            # Prüfe ob bereits eliminiert
            existing = EliminatedTeam.query.filter_by(
                user_id=loser_usage.user_id, 
                team_id=loser_usage.team_id
            ).first()
            
            if not existing:
                elimination = EliminatedTeam(
                    user_id=loser_usage.user_id,
                    team_id=loser_usage.team_id
                )
                db.session.add(elimination)
                
                user = User.query.get(loser_usage.user_id)
                team = Team.query.get(loser_usage.team_id)
                print(f"➕ Eliminiert: {team.name} für {user.username} (als Verlierer)")
        
        db.session.commit()
        
        # Zeige Ergebnis
        print("\n=== ELIMINIERUNGEN PRO BENUTZER ===")
        users = User.query.all()
        for user in users:
            eliminations = EliminatedTeam.query.filter_by(user_id=user.id).all()
            print(f"{user.username}: {len(eliminations)} eliminierte Teams")
            for elim in eliminations:
                print(f"  - {elim.team.name}")
        
        print("\n✅ Eliminierungen erfolgreich korrigiert!")

if __name__ == '__main__':
    fix_eliminations()

