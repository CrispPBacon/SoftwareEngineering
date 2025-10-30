from . import db


class ShowcaseImage(db.Model):
    __tablename__ = 'showcase_images'
    showcase_image_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    image_url = db.Column(db.String(500), nullable=False)
    # Marks if an image is removed
    removed = db.Column(db.Boolean, default=False)
