def generate_model(controller_name: str) -> str:
    split_controller_name = controller_name.split("_")
    capitalized_controller_name = "".join(
        [word.capitalize() for word in split_controller_name]
    )
    template = f"""from pydantic import BaseModel
    
    
class {capitalized_controller_name}(BaseModel):
    name: str
    """
    return template
