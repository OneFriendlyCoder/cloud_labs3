import os
from flask import Blueprint, render_template, request, current_app, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
def view_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
        
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    
    profile_pic = None
    for ext in ['png', 'jpg', 'jpeg']:
        if os.path.exists(os.path.join(upload_folder, f"{user_id}_profile_picture.{ext}")):
            profile_pic = f"{user_id}_profile_picture.{ext}"
            break
            
    if request.method == "POST":
        if 'profile_pic' not in request.files:
            return redirect(request.url)
        file = request.files['profile_pic']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
            filename = f"{user_id}_profile_picture.{ext}"
            
            # Remove old ones
            for old_ext in ['png', 'jpg', 'jpeg']:
                old_path = os.path.join(upload_folder, f"{user_id}_profile_picture.{old_ext}")
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            file.save(os.path.join(upload_folder, filename))
            return redirect(url_for('profile.view_profile'))
            
    return render_template("profile.html", profile_pic=profile_pic, user_id=user_id)

@profile_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
