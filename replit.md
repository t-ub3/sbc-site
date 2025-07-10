# SBC News Website - Replit Configuration

## Overview

This is a Flask-based news website for the Stepford Broadcasting Corporation (SBC). The application provides a content management system for creating, editing, and publishing news articles with role-based access control for administrators and contributors.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive design
- **Static Assets**: CSS and JavaScript files served from `/static/`
- **Rich Text Editor**: TinyMCE integration for article content creation
- **Styling**: Custom CSS with SBC brand colors and Bootstrap components

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Authentication**: Flask-Login for session management
- **Forms**: Flask-WTF with WTForms for form handling and validation
- **Security**: Werkzeug for password hashing and ProxyFix middleware

### Database Design
- **Users**: Stores user accounts with roles (admin/tenant), names, and credentials
- **Articles**: Main content with title, content, summary, publication status, and breaking news flags
- **Categories**: Article categorization system
- **Departments**: Optional departmental organization for articles
- **Relationships**: Foreign key relationships between users, articles, categories, and departments

## Key Components

### Models (models.py)
- **User**: UserMixin integration for authentication, role-based permissions
- **Article**: Core content model with publishing workflow
- **Category**: Article classification system
- **Department**: Optional organizational structure

### Authentication System
- **Login/Logout**: Session-based authentication with Flask-Login
- **Role-based Access**: Admin vs. contributor permissions
- **Registration**: Admin-only user creation functionality

### Content Management
- **Article CRUD**: Create, read, update, delete operations for articles
- **Publishing Workflow**: Draft and published states with breaking news support
- **Rich Text Editing**: TinyMCE integration for content creation
- **Category Management**: Dynamic category and department administration

### User Interface
- **Public Views**: Homepage, category pages, and individual article pages
- **Dashboard**: Administrative interface for content management
- **Responsive Design**: Bootstrap-based mobile-friendly interface

## Data Flow

1. **Authentication Flow**: Users log in → Flask-Login creates session → Role-based access control applied
2. **Content Creation**: Contributors create articles → Admin approval workflow → Publication
3. **Content Display**: Public users browse articles → Category filtering → Individual article views
4. **Administration**: Admins manage users, categories, and content through dashboard interface

## External Dependencies

### Python Packages
- **Flask**: Web framework and core functionality
- **Flask-SQLAlchemy**: Database ORM and migrations
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **Werkzeug**: Security utilities and middleware
- **python-dotenv**: Environment variable management

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **TinyMCE**: Rich text editor for article content
- **Custom CSS**: SBC branding and additional styling

### Database Configuration
- **Default**: SQLite for development (`sbc_news.db`)
- **Production**: Configurable via `DATABASE_URL` environment variable
- **Connection Pooling**: SQLAlchemy engine options for connection management

## Deployment Strategy

### Environment Configuration
- **Secret Key**: Configurable via `SESSION_SECRET` environment variable
- **Database URL**: Flexible database configuration through environment variables
- **Debug Mode**: Development settings with detailed error reporting

### Production Considerations
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments
- **Connection Pooling**: Database connection management with pool recycling
- **Security**: Environment-based secret key management

### Development Setup
- **Entry Point**: `main.py` runs the Flask development server
- **Debug Mode**: Enabled by default for development
- **Host Configuration**: Bound to `0.0.0.0:5000` for container compatibility

### Missing Components
The application structure is mostly complete but may need:
- Database initialization and migration scripts
- Complete route implementations (some routes referenced but not fully implemented)
- Error handling and logging configuration
- Static file optimization for production
- Session configuration and security headers