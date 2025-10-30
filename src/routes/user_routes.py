from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, flash, session, render_template, redirect, url_for, jsonify
from ..models import User, db
from ..services import send_token_to_email, generate_token, confirm_token, send_reset_email

user_bp = Blueprint('user', __name__)


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f'Attempting login with username: {username}')
        try:
            # Use the snake_case column name 'username'
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.user_id
                session['role'] = user.role.lower()
                print(
                    f'Login successful for user: {username}, role: {user.role}')
                return redirect(url_for('main.menu'))
            else:
                flash('Invalid username or password', 'error')
                print(
                    f'Invalid username or password for user: {username}')
        except Exception as e:
            flash(f'An error occurred during login: {str(e)}', 'error')
            print(f'Error during login: {str(e)}')
    return render_template('login.html')


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Fetching form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            gender = request.form.get('gender', '').strip()
            email = request.form.get('email', '').strip()
            number = request.form.get('number', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            # Collect validation errors
            errors = []
            if not first_name:
                errors.append('First name is required.')
            if not last_name:
                errors.append('Last name is required.')
            if gender not in ['Male', 'Female', 'LGBT+']:
                errors.append('Please select a valid gender.')
            if not email or '@' not in email:
                errors.append('A valid email address is required.')
            if not number or not number.isdigit():
                errors.append('Phone number must contain only digits.')
            if not username:
                errors.append('Username is required.')
            if not password or len(password) < 6:
                errors.append('Password must be at least 6 characters long.')

            # Display errors and reload the form if there are any
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('register.html')

            # Create new user
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                email=email,
                phone_number=number,
                username=username,
                role='user'
            )
            new_user.set_password(password)

            # Save to the database
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user.login'))

        except IntegrityError as e:
            db.session.rollback()
            print(
                f"Integrity error during registration: {str(e)}")
            if 'username' in str(e.orig).lower():
                flash('Username is already taken. Please try another.', 'error')
            elif 'email' in str(e.orig).lower():
                flash('Email is already registered. Please use another.', 'error')
            else:
                flash('An integrity error occurred. Please try again.', 'error')
        except Exception as e:
            print(
                f"Unexpected error during registration: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'error')

    return render_template('register.html')


@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.', 'error')
        return redirect(url_for('user.login'))
    # Retrieve the logged-in user's data
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('user.login'))
    # Allow admins to access their profile
    if user.role == 'admin':
        flash('You are an admin. Ensure to update your profile accordingly.', 'info')
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get(
                'first_name', user.first_name).strip()
            last_name = request.form.get('last_name', user.last_name).strip()
            gender = request.form.get('gender', user.gender)
            email = request.form.get('email', user.email).strip()
            phone_number = request.form.get(
                'number', user.phone_number).strip()
            username = request.form.get('username', user.username).strip()
            current_password = request.form.get('current_password')
            password = request.form.get('password')
            # Validate input data
            if not all([first_name, last_name, gender, email, phone_number, username]):
                flash('All fields except password are required.', 'error')
                return render_template('profile.html', user=user)
            if '@' not in email:
                flash('Invalid email address.', 'error')
                return render_template('profile.html', user=user)
            if not phone_number.isdigit():
                flash('Phone number must contain only digits.', 'error')
                return render_template('profile.html', user=user)
            # Update user details
            user.first_name = first_name
            user.last_name = last_name
            user.gender = gender
            user.email = email
            user.phone_number = phone_number
            user.username = username
            # Conditionally update the password if provided
            if password:
                if len(password) < 6:
                    flash('Password must be at least 6 characters long.', 'error')
                    return render_template('profile.html', user=user)
                if not user.check_password(current_password):
                    flash('You entered the wrong current password!', 'error')
                    return render_template('profile.html', user=user)
                user.set_password(password)
            # Commit changes to the database
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except IntegrityError as e:
            db.session.rollback()
            if 'unique constraint' in str(e.orig).lower():
                flash(
                    'Username or Email already exists, please try a different one.', 'error')
            else:
                flash(f'Error updating profile: {str(e)}', 'error')
        except Exception as e:
            db.session.rollback()
            print(f"Error updating profile: {str(e)}")
            flash('An unexpected error occurred. Please try again later.', 'error')
    return render_template('profile.html', user=user)


@user_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('user.login'))


@user_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_token(email)
            send_reset_email(email, token)
            flash('Reset link sent to your email.', 'success')
        else:
            flash('No account found with that email.', 'error')

        return redirect(url_for("user.forgot_password"))

    return render_template('forgot_password.html')


@user_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token)
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('user.forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('user.login'))
    return render_template('reset_password.html')
