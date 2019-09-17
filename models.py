# models.py 
 
from scorer_app import db

class Score(db.Model):
    """Model for team scores."""

    __tablename__ = 'Scores'
    id = db.Column(db.Integer,
                   primary_key=True)
    team_name = db.Column(db.String(64),
                         index=False,
                         unique=True,
                         nullable=False)
    email = db.Column(db.String(80),
                      index=True,
                      unique=True,
                      nullable=False)
    created = db.Column(db.DateTime,
                        index=False,
                        unique=False,
                        nullable=False)
    bio = db.Column(db.Text,
                    index=False,
                    unique=False,
                    nullable=True)
    admin = db.Column(db.Boolean,
                      index=False,
                      unique=False,
                      nullable=False)

 
class Artist(db.Model):
    __tablename__ = "artists"
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
 
    def __repr__(self):
        return "<Artist: {}>".format(self.name)
 
 
class Album(db.Model):
    """"""
    __tablename__ = "albums"
 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    release_date = db.Column(db.String)
    publisher = db.Column(db.String)
    media_type = db.Column(db.String)
 
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"))
    artist = db.relationship("Artist", backref=db.backref(
        "albums", order_by=id), lazy=True)