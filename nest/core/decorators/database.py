from fastapi.exceptions import HTTPException


def db_request_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
            self.session.close()
            return result
        except Exception as e:
            self.session.rollback()
            self.session.close()
            print(f"Error in {func.__name__}: {str(e)}")
            return HTTPException(status_code=500, detail=str(e))

    return wrapper
