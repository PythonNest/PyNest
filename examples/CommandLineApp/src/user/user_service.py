from nest.core import Injectable


@Injectable
class UserService:

    def get_users(self):
        print("This command show all users")

    def get_user(self, user_name: str):
        print(f"This command show user with user_name: {user_name}")
