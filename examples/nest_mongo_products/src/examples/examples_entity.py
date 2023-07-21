from beanie import Document
        
        
class Examples(Document):
    name: str
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Example Name",
            }
        }
