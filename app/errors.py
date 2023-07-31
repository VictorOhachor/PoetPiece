from flask import render_template, current_app, request, redirect, flash
from sqlalchemy.exc import OperationalError


@current_app.errorhandler(OperationalError)
def handle_db_connection_error(e):
    print(e.description)
    flash('Database connection failed; retrying...', 'error')
    redirect(request.url)


@current_app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template(
        'errors/404.html', err_desc=f'The path - {request.path} - you requested was not found'
    ), 404


@current_app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 or server errors."""
    return render_template('errors/500.html', err_desc=e.description), 500
