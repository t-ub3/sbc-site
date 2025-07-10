from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Article, Category, Department
from forms import LoginForm, RegisterForm, ArticleForm, CategoryForm, DepartmentForm, ProfileForm
from utils import admin_required, format_datetime, truncate_text

# Add template filters
app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['truncate'] = truncate_text

@app.route('/')
def index():
    """Homepage with latest news"""
    # Get breaking news
    breaking_news = Article.query.filter_by(is_breaking=True, published=True).first()
    
    # Get latest articles
    articles = Article.query.filter_by(published=True).order_by(Article.created_at.desc()).limit(20).all()
    
    # Get categories for navigation
    categories = Category.query.all()
    
    return render_template('index.html', articles=articles, breaking_news=breaking_news, categories=categories)

@app.route('/category/<int:category_id>')
def category(category_id):
    """Show articles in a specific category"""
    category = Category.query.get_or_404(category_id)
    articles = Article.query.filter_by(category_id=category_id, published=True).order_by(Article.created_at.desc()).all()
    categories = Category.query.all()
    breaking_news = Article.query.filter_by(is_breaking=True, published=True).first()
    
    return render_template('category.html', category=category, articles=articles, categories=categories, breaking_news=breaking_news)

@app.route('/article/<int:article_id>')
def article(article_id):
    """Show individual article"""
    article = Article.query.get_or_404(article_id)
    
    # Only show published articles to non-admin users
    if not article.published and (not current_user.is_authenticated or not current_user.is_admin()):
        abort(404)
    
    categories = Category.query.all()
    breaking_news = Article.query.filter_by(is_breaking=True, published=True).first()
    
    return render_template('article.html', article=article, categories=categories, breaking_news=breaking_news)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    """Register new tenant user (admin only)"""
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email address already registered', 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            email=form.email.data,
            name=form.name.data,
            password_hash=generate_password_hash(form.password.data),
            role='tenant'
        )
        db.session.add(user)
        db.session.commit()
        
        flash('User registered successfully', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('index'))

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    if current_user.is_admin():
        # Admin sees all articles
        articles = Article.query.order_by(Article.created_at.desc()).limit(10).all()
        total_articles = Article.query.count()
        published_articles = Article.query.filter_by(published=True).count()
        total_users = User.query.count()
    else:
        # Tenant sees only their articles
        articles = Article.query.filter_by(author_id=current_user.id).order_by(Article.created_at.desc()).limit(10).all()
        total_articles = Article.query.filter_by(author_id=current_user.id).count()
        published_articles = Article.query.filter_by(author_id=current_user.id, published=True).count()
        total_users = None
    
    return render_template('dashboard/dashboard.html', 
                         articles=articles, 
                         total_articles=total_articles,
                         published_articles=published_articles,
                         total_users=total_users)

@app.route('/dashboard/create-article', methods=['GET', 'POST'])
@login_required
def create_article():
    """Create new article"""
    form = ArticleForm()
    if form.validate_on_submit():
        # Log the form data for debugging
        app.logger.info(f"Creating article with published={form.published.data}")
        
        article = Article(
            title=form.title.data,
            content=form.content.data,
            summary=form.summary.data,
            category_id=form.category_id.data,
            department_id=form.department_id.data if form.department_id.data != 0 else None,
            published=form.published.data,
            is_breaking=form.is_breaking.data,
            breaking_message=form.breaking_message.data,
            author_id=current_user.id
        )
        
        # If this is breaking news, unset other breaking news
        if form.is_breaking.data:
            Article.query.filter_by(is_breaking=True).update({'is_breaking': False})
        
        db.session.add(article)
        db.session.commit()
        
        # Log the final state for debugging
        app.logger.info(f"Article created with ID={article.id}, published={article.published}")
        
        flash('Article created successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('dashboard/create_article.html', form=form)

@app.route('/dashboard/edit-article/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    """Edit existing article"""
    article = Article.query.get_or_404(article_id)
    
    # Check permissions
    if not current_user.is_admin() and article.author_id != current_user.id:
        abort(403)
    
    form = ArticleForm(obj=article)
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        article.summary = form.summary.data
        article.category_id = form.category_id.data
        article.department_id = form.department_id.data if form.department_id.data != 0 else None
        article.published = form.published.data
        article.is_breaking = form.is_breaking.data
        article.breaking_message = form.breaking_message.data
        
        # If this is breaking news, unset other breaking news
        if form.is_breaking.data:
            Article.query.filter(Article.id != article_id).update({'is_breaking': False})
        
        db.session.commit()
        flash('Article updated successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('dashboard/edit_article.html', form=form, article=article)

@app.route('/dashboard/delete-article/<int:article_id>', methods=['POST'])
@login_required
def delete_article(article_id):
    """Delete article"""
    article = Article.query.get_or_404(article_id)
    
    # Check permissions
    if not current_user.is_admin() and article.author_id != current_user.id:
        abort(403)
    
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard/manage-users')
@admin_required
def manage_users():
    """Manage users (admin only)"""
    users = User.query.all()
    return render_template('dashboard/manage_users.html', users=users)

@app.route('/dashboard/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting admin user
    if user.is_admin():
        flash('Cannot delete admin user', 'error')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('manage_users'))

@app.route('/dashboard/manage-categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    """Manage categories (admin only)"""
    form = CategoryForm()
    if form.validate_on_submit():
        # Check if category already exists
        if Category.query.filter_by(name=form.name.data).first():
            flash('Category already exists', 'error')
        else:
            category = Category(name=form.name.data)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully', 'success')
        return redirect(url_for('manage_categories'))
    
    categories = Category.query.all()
    departments = Department.query.all()
    dept_form = DepartmentForm()
    
    return render_template('dashboard/manage_categories.html', 
                         form=form, 
                         categories=categories, 
                         departments=departments,
                         dept_form=dept_form)

@app.route('/dashboard/add-department', methods=['POST'])
@admin_required
def add_department():
    """Add new department (admin only)"""
    form = DepartmentForm()
    if form.validate_on_submit():
        # Check if department already exists
        if Department.query.filter_by(name=form.name.data).first():
            flash('Department already exists', 'error')
        else:
            department = Department(name=form.name.data)
            db.session.add(department)
            db.session.commit()
            flash('Department added successfully', 'success')
    
    return redirect(url_for('manage_categories'))

@app.route('/dashboard/delete-category/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    """Delete category (admin only)"""
    category = Category.query.get_or_404(category_id)
    
    # Check if category has articles
    if category.articles:
        flash('Cannot delete category with articles', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully', 'success')
    
    return redirect(url_for('manage_categories'))

@app.route('/dashboard/delete-department/<int:department_id>', methods=['POST'])
@admin_required
def delete_department(department_id):
    """Delete department (admin only)"""
    department = Department.query.get_or_404(department_id)
    
    # Remove department from articles but don't delete articles
    for article in department.articles:
        article.department_id = None
    
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully', 'success')
    return redirect(url_for('manage_categories'))

@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Edit user profile"""
    form = ProfileForm(obj=current_user)
    
    # Non-admin users cannot edit role title
    if not current_user.is_admin():
        form.role_title.render_kw = {'readonly': True}
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        if current_user.is_admin():
            current_user.role_title = form.role_title.data
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('dashboard/profile.html', form=form)

@app.errorhandler(404)
def not_found(error):
    categories = Category.query.all()
    breaking_news = Article.query.filter_by(is_breaking=True, published=True).first()
    return render_template('404.html', categories=categories, breaking_news=breaking_news), 404

@app.errorhandler(403)
def forbidden(error):
    categories = Category.query.all()
    breaking_news = Article.query.filter_by(is_breaking=True, published=True).first()
    return render_template('403.html', categories=categories, breaking_news=breaking_news), 403
