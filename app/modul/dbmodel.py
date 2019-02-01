from app import db


class Sentiment(db.Model):
    __tablename__ = 'sentiment'

    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    tahun_ajaran = db.Column(db.String, nullable=False)
    positive = db.Column(db.Float, nullable=False)
    neutral = db.Column(db.Float, nullable=False)
    negative = db.Column(db.Float, nullable=False)

    def __init__(self, tahun_ajaran, positive, neutral, negative):
        self.tahun_ajaran = tahun_ajaran
        self.positive = positive
        self.neutral = neutral
        self.negative = negative

    def __repr__(self):
        return "<Tahun Ajaran: {}".format(self.tahun_ajaran)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getAll():
        return Sentiment.query.all()
