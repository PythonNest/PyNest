from nest.core.decorators import Controller , Get

@Controller('app')
class AppController: 
    
    @Get('/hello')
    def hello(): 
      return "Hello, world!"