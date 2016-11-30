# Decorator takes an Exception class, and is invoked everytime the exception is raised
@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])