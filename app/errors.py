from flask import render_template, current_app

@current_app.errorhandler(404,)
def page_not_found(e):
    """Handle 404 errors."""
    err_desc = e.description
    return render_template('errors/404.html', err_desc=err_desc), 404


@current_app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 or server errors."""
    err_desc = e.description
    return render_template('errors/500.html', err_desc=err_desc), 500

@current_app.errorhandler(401)
def unauthorized_error(e):
    """Handle errors that occur when users are not authorized."""
    err_desc = 'You are unauthorized. Login/Sign up if you are not authenticated.'
    return render_template('errors/401.html', err_desc=err_desc), 401
