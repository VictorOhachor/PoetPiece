from flask import render_template, current_app, request, redirect, url_for, flash
from sqlalchemy.exc import OperationalError
from .helpers.cleanup import failed_posts, lock
import time


@current_app.errorhandler(OperationalError)
def handle_db_connection_error(e):
    if request.method == 'GET':
        return redirect(request.url)
    
    # Generate a unique hash for the request data to use as an idempotency key
    data_hash = hash(frozenset(request.form.items()))

    if data_hash in failed_posts:
        flash('There was a server timeout, but it has been resolved', 'error')
        return redirect(request.url)
    
    with lock:
        # Mark the data as failed
        failed_posts[data_hash] = time.time()

    flash('Database connection failed; retrying...', 'error')
    return redirect(request.referrer)


@current_app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template(
        'errors/404.html', err_desc=f'The path you requested was not found'
    ), 404


@current_app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 or server errors."""
    return render_template('errors/500.html', err_desc=e.description), 500
