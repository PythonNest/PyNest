from nest.core import PyNestFactory
from app_module import AppModule


app = PyNestFactory.create( 
    AppModule,
    description="This is my FastAPI app.", title="My App", version="1.0.0", debug=True)
http_server = app.get_server()

