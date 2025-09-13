"""
NEUE PICK-API MIT KORREKTER LOGIK
Basierend auf dem vollständigen Regelwerk
"""

@app.route('/api/picks', methods=['GET', 'POST'])
def handle_picks():
    try:
        if request.method == 'GET':
            # GET-Logik bleibt unverändert
            user_id = request.args.get('user_id', type=int)
            week = request.args.get('week', type=int)
            
            if not user_id:
                return jsonify({'error': 'User ID required'}), 400
                
            query = Pick.query.filter_by(user_id=user_id)
            
            if week:
                picks = query.join(Match).filter(Match.week == week).all()
            else:
                picks = query.all()
                
            return jsonify({
                'picks': [pick.to_dict() for pick in picks]
            }), 200
        
        elif request.method == 'POST':
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'Not authenticated'}), 401
                
            data = request.get_json()
            match_id = data.get('match_id')
            chosen_team_id = data.get('chosen_team_id')
            
            if not match_id or not chosen_team_id:
                return jsonify({'error': 'Match ID and chosen team ID required'}), 400
            
            # === BASIC VALIDATIONS ===
            match = Match.query.get(match_id)
            if not match:
                return jsonify({'error': 'Match not found'}), 404
            
            team = Team.query.get(chosen_team_id)
            if not team:
                return jsonify({'error': 'Team not found'}), 404
            
            # Check if team is part of the match
            if team.id not in [match.home_team_id, match.away_team_id]:
                return jsonify({'error': 'Team is not part of this match'}), 400
            
            # Check if game has started
            if match.is_game_started:
                return jsonify({'error': 'Game has already started. Picks are no longer allowed.'}), 400
            
            # Check if match is completed
            if match.is_completed:
                return jsonify({'error': 'Cannot pick for completed match'}), 400
            
            # === DETERMINE OPPOSING TEAM ===
            opposing_team_id = match.away_team_id if team.id == match.home_team_id else match.home_team_id
            
            # === ELIMINATION CHECKS ===
            # Check if chosen team is winner-eliminated
            winner_eliminated = EliminatedTeam.query.filter_by(
                user_id=user_id, 
                team_id=team.id, 
                elimination_type='winner'
            ).first()
            if winner_eliminated:
                return jsonify({'error': f'{team.name} cannot be picked as winner (already used 2x as winner)'}), 400
            
            # Check if opposing team is loser-eliminated
            loser_eliminated = EliminatedTeam.query.filter_by(
                user_id=user_id, 
                team_id=opposing_team_id, 
                elimination_type='loser'
            ).first()
            if loser_eliminated:
                opposing_team = Team.query.get(opposing_team_id)
                return jsonify({'error': f'{opposing_team.name} cannot be picked as loser (already used 1x as loser)'}), 400
            
            # === USAGE LIMIT CHECKS ===
            # Check winner usage limit (max 2x)
            winner_usage = TeamWinnerUsage.query.filter_by(user_id=user_id, team_id=team.id).first()
            if winner_usage and winner_usage.usage_count >= 2:
                return jsonify({'error': f'{team.name} has already been picked as winner 2 times this season'}), 400
            
            # Check loser usage limit (max 1x)
            loser_usage = TeamLoserUsage.query.filter_by(user_id=user_id, team_id=opposing_team_id).first()
            if loser_usage:
                opposing_team = Team.query.get(opposing_team_id)
                return jsonify({'error': f'{opposing_team.name} has already been picked as loser this season'}), 400
            
            # === HANDLE PICK (CREATE OR UPDATE) ===
            existing_week_pick = Pick.query.join(Match).filter(
                Pick.user_id == user_id,
                Match.week == match.week
            ).first()
            
            if existing_week_pick:
                # UPDATE EXISTING PICK (Pick-Wechsel)
                result = update_existing_pick(user_id, existing_week_pick, match, team.id, opposing_team_id)
                if result.get('error'):
                    return jsonify(result), 400
                    
                return jsonify({
                    'message': 'Pick updated successfully',
                    'pick': existing_week_pick.to_dict()
                }), 200
            else:
                # CREATE NEW PICK
                result = create_new_pick(user_id, match, team.id, opposing_team_id)
                if result.get('error'):
                    return jsonify(result), 400
                    
                return jsonify({
                    'message': 'Pick created successfully',
                    'pick': result['pick'].to_dict()
                }), 201
                
    except Exception as e:
        print(f"Error in handle_picks: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


def update_existing_pick(user_id, existing_pick, new_match, new_team_id, new_opposing_team_id):
    """
    Update existing pick - nur bei laufenden Spielen, nicht bei abgeschlossenen
    """
    try:
        old_match = existing_pick.match
        old_team_id = existing_pick.chosen_team_id
        old_opposing_team_id = old_match.away_team_id if old_team_id == old_match.home_team_id else old_match.home_team_id
        
        # Wenn sich nichts ändert, nichts tun
        if existing_pick.match_id == new_match.id and old_team_id == new_team_id:
            return {'success': True}
        
        # WICHTIG: Nur bei nicht-abgeschlossenen Spielen Usage zurücksetzen
        if not old_match.is_completed:
            # Entferne alte Usage-Einträge (nur bei laufenden Spielen)
            remove_temporary_usage(user_id, old_team_id, old_opposing_team_id, old_match.id)
        
        # Update Pick
        existing_pick.match_id = new_match.id
        existing_pick.chosen_team_id = new_team_id
        
        # Füge neue Usage-Einträge hinzu (nur bei laufenden Spielen)
        if not new_match.is_completed:
            add_temporary_usage(user_id, new_team_id, new_opposing_team_id, new_match)
        
        db.session.commit()
        return {'success': True}
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Failed to update pick: {str(e)}'}


def create_new_pick(user_id, match, team_id, opposing_team_id):
    """
    Create new pick
    """
    try:
        # Create pick
        new_pick = Pick(
            user_id=user_id,
            match_id=match.id,
            chosen_team_id=team_id
        )
        db.session.add(new_pick)
        
        # Add temporary usage (nur bei laufenden Spielen)
        if not match.is_completed:
            add_temporary_usage(user_id, team_id, opposing_team_id, match)
        
        db.session.commit()
        return {'success': True, 'pick': new_pick}
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Failed to create pick: {str(e)}'}


def add_temporary_usage(user_id, team_id, opposing_team_id, match):
    """
    Füge temporäre Usage-Einträge hinzu (werden bei Spielende finalisiert)
    """
    # Winner usage
    winner_usage = TeamWinnerUsage.query.filter_by(user_id=user_id, team_id=team_id).first()
    if winner_usage:
        winner_usage.usage_count += 1
    else:
        winner_usage = TeamWinnerUsage(user_id=user_id, team_id=team_id, usage_count=1)
        db.session.add(winner_usage)
    
    # Loser usage
    loser_usage = TeamLoserUsage(
        user_id=user_id,
        team_id=opposing_team_id,
        week=match.week,
        match_id=match.id
    )
    db.session.add(loser_usage)


def remove_temporary_usage(user_id, team_id, opposing_team_id, match_id):
    """
    Entferne temporäre Usage-Einträge (bei Pick-Wechsel)
    """
    # Remove winner usage
    winner_usage = TeamWinnerUsage.query.filter_by(user_id=user_id, team_id=team_id).first()
    if winner_usage:
        winner_usage.usage_count -= 1
        if winner_usage.usage_count <= 0:
            db.session.delete(winner_usage)
    
    # Remove loser usage
    loser_usage = TeamLoserUsage.query.filter_by(
        user_id=user_id, 
        team_id=opposing_team_id, 
        match_id=match_id
    ).first()
    if loser_usage:
        db.session.delete(loser_usage)

