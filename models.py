from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Club(db.Model):
    __tablename__ = 'clubs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    members = db.relationship('Member', backref='club', lazy='dynamic',
                              cascade='all, delete-orphan')


class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    display_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    avatar = db.Column(db.String(256), nullable=True)
    score = db.Column(db.Float, nullable=False, default=0.0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    score_changes = db.relationship('ScoreChange', backref='member', lazy='dynamic',
                                    cascade='all, delete-orphan')

    __table_args__ = (db.UniqueConstraint('club_id', 'display_id'),)


class ScoreChange(db.Model):
    __tablename__ = 'score_changes'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    old_score = db.Column(db.Float, nullable=False)
    new_score = db.Column(db.Float, nullable=False)
    change_type = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    is_self_confirmed = db.Column(db.Boolean, nullable=False, default=True)
    status = db.Column(db.String(20), nullable=False, default='approved')
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    applicant = db.relationship('User', foreign_keys=[applicant_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])


class ViewRequest(db.Model):
    __tablename__ = 'view_requests'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_self_confirmed = db.Column(db.Boolean, nullable=False, default=True)
    not_self_reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    member = db.relationship('Member', foreign_keys=[member_id])
    applicant = db.relationship('User', foreign_keys=[applicant_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

    __table_args__ = (db.UniqueConstraint('member_id', 'applicant_id'),)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # super_admin / admin / user
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @property
    def is_admin(self):
        return self.role in ('admin', 'super_admin')

    @property
    def is_super_admin(self):
        return self.role == 'super_admin'

    @property
    def role_display(self):
        return {'super_admin': '超级管理员', 'admin': '管理员', 'user': '普通用户'}.get(self.role, '未知')
