from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

#error handler function for 404 error pages
@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404 #this second value is the status code for the error response

#error handler function for 404 error pages
@errors.app_errorhandler(403)
def error_404(error):
    return render_template('errors/403.html'), 403

#error handler function for 404 error pages
@errors.app_errorhandler(500)
def error_404(error):
    return render_template('errors/405.html'), 500