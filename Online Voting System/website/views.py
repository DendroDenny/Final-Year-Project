from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Vote
from . import db
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot_detector import check_bot_email

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  
            db.session.add(new_note) 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/castvote', methods=['GET', 'POST'])
@login_required
def cast_vote():
    if request.method == 'POST':
        voted_candidate = request.form.get('voted_candidate')  # Rename the variable to avoid conflict

        if not voted_candidate:
            flash('Please choose 1 candidate!', category='error')
        else:
            # Check if the user has already voted (optional, based on your requirements)
            existing_vote = Vote.query.filter_by(user_id=current_user.id).first()
            if existing_vote:
                flash('You have already voted!', category='error')
            else:
                # Create a new vote with IP tracking
                new_vote = Vote(
                    voted_candidate=voted_candidate, 
                    user_id=current_user.id,
                    ip_address=request.remote_addr
                )
                db.session.add(new_vote)
                db.session.commit()
                
                # Check if user email is from a bot
                try:
                    is_bot, confidence = check_bot_email(current_user.email)
                    if is_bot and confidence > 0.7:
                        flash('Vote recorded. Account flagged for verification.', category='warning')
                    else:
                        flash('Vote Casted!', category='success')
                except Exception as e:
                    flash('Vote Casted!', category='success')  # Fail gracefully

    return render_template("home.html", user=current_user)


