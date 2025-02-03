from flask import Flask, render_template, request, redirect, jsonify, json, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Date, Integer, String, Row
from sqlalchemy import *
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_remembered, login_required
from flask_socketio import SocketIO, emit, join_room, leave_room