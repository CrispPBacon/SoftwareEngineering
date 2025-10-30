from flask import session


def inject_role():
    """Injects the user's role into all templates."""
    role = session.get('role')
    return dict(role=role)
