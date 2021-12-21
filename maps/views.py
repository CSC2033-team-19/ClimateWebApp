# Import modules
from app import db
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user, login_required
import logging
from models import Events