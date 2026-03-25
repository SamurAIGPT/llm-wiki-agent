from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, ForeignKey, MetaData
from flask_login import UserMixin

from flask import Flask

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
app = Flask(__name__)
    
class Agent_Session(db.Model):
    __tablename__ = "agent_session"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_1 = db.Column(db.String(200), default="", server_default = "")
    role_2 = db.Column(db.String(200), default="", server_default = "")
    task = db.Column(db.String(3000), default="", server_default = "")
    user_store = db.Column(db.String, default="", server_default = "")
    assistant_store = db.Column(db.String, default="", server_default = "")
    admin_id = db.Column(db.String(100), ForeignKey("admin.id"), index=True)    

class Admin(UserMixin,db.Model):
    __tablename__ = "admin"
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, index=True)  
    google_id = db.Column(db.String(100))
    openai_key = db.Column(db.String(100))
    minimax_key = db.Column(db.String(200))
    llm_provider = db.Column(db.String(50), default="openai", server_default="openai")
    profile_image = db.Column(db.String(100000))
    password = db.Column(db.String(100))
    created_date = db.Column(DateTime)
    gpt_model = db.Column(db.String, default="gpt-3.5-turbo", server_default="gpt-3.5-turbo")
    agent_sessions = db.relationship('Agent_Session', backref='admin',
                                      cascade="all,delete", lazy='dynamic')                                      
    def get_id(self):
        return (self.id)