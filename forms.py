from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, BooleanField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from models import Category, Department

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    summary = TextAreaField('Summary/Excerpt', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[Optional()])
    published = BooleanField('Publish immediately')
    is_breaking = BooleanField('Mark as breaking news')
    breaking_message = StringField('Breaking news message', validators=[Optional(), Length(max=200)])
    
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
        self.department_id.choices = [(0, 'None')] + [(d.id, d.name) for d in Department.query.all()]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(min=2, max=50)])

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    role_title = StringField('Role Title', validators=[Optional(), Length(max=100)])
