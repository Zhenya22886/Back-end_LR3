from datetime import datetime, timezone

from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    records = db.relationship(
        "Record",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    account = db.relationship(
        "Account",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.id} {self.name!r}>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)

    records = db.relationship(
        "Record",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Category {self.id} {self.name!r}>"


class Record(db.Model):
    

    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    user = db.relationship("User", back_populates="records")
    category = db.relationship("Category", back_populates="records")

    def __repr__(self) -> str:
        return (
            f"<Record {self.id} "
            f"user={self.user_id} category={self.category_id} "
            f"amount={self.amount}>"
        )


class Account(db.Model):
    

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    balance = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0,
    )

    user = db.relationship("User", back_populates="account")

    def __repr__(self) -> str:
        return f"<Account {self.id} user={self.user_id} balance={self.balance}>"
