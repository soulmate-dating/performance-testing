import random
from locust import TaskSet, task, between, User, FastHttpUser
import faker

allEmails = []

fake_gen = faker.Faker()
genders = ['man', 'woman']
preferences = ['man', 'woman', 'anyone']
habits = ['no', 'sometimes', 'yes', 'prefer not to say']
intentions = ['life partner', 'long-term relationship', 'short-term relationship', 'friendship', 'figuring it out',
              'prefer not to say']
family_plans = ['do not want children', 'want children', 'open to children', 'not sure yet', 'prefer not to say']


class UserBehavior(TaskSet):

    def __init__(self, parent: User):
        super().__init__(parent)
        self.email = fake_gen.email()
        self.gender = genders[random.randint(0, len(genders) - 1)]
        if self.gender == "man":
            self.first_name = fake_gen.first_name_male()
            self.last_name = fake_gen.last_name_male()
        else:
            self.first_name = fake_gen.first_name_female()
            self.last_name = fake_gen.last_name_female()
        self.birth_date = str(fake_gen.date_of_birth(minimum_age=18, maximum_age=69))
        self.allPrompts = []
        self.prompt_ids = []
        while self.email in allEmails:
            self.email = fake_gen.email()
        allEmails.append(self.email)
        self.password = fake_gen.password()
        self.token = ""
        self.refresh_token = ""
        self.user_id = ""

    def on_start(self):
        self.signup()
        self.create_profile()
        self.create_prompt()

    def signup(self):
        with self.client.post("/api/v0/auth/signup", json={
            "email": self.email,
            "password": self.password
        }) as response:
            if response.status_code != 201:
                print("signup", response.json(), response.status_code)
            else:
                self.token = response.json()['data']['access_token']
                self.refresh_token = response.json()['data']['refresh_token']
                self.user_id = response.json()['data']['id']

    def create_profile(self):
        self.client.post(f"/api/v0/users/{self.user_id}/profile", headers={"Authorization": f"Bearer {self.token}"},
                         json={
                             "first_name": self.first_name,
                             "last_name": self.last_name,
                             "birth_date": self.birth_date,
                             "drinks_alcohol": habits[random.randint(0, len(habits) - 1)],
                             "family_plans": family_plans[random.randint(0, len(family_plans) - 1)],
                             "has_children": fake_gen.boolean(),
                             "height": random.randint(150, 200),
                             "intention": intentions[random.randint(0, len(intentions) - 1)],
                             "location": "California",
                             "preferred_partner": preferences[random.randint(0, len(preferences) - 1)],
                             "sex": genders[random.randint(0, len(genders) - 1)],
                             "smokes": habits[random.randint(0, len(habits) - 1)],
                         }, catch_response=True)

    @task(1)
    def login(self):
        with self.client.post("/api/v0/auth/login", json={
            "email": self.email,
            "password": self.password
        }) as response:
            if response.status_code != 200:
                print("login", response.json(), response.status_code)
            else:
                self.token = response.json()['data']['access_token']
                self.refresh_token = response.json()['data']['refresh_token']
                self.user_id = response.json()['data']['id']

    @task(2)
    def refresh(self):
        with self.client.get("/api/v0/auth/refresh",
                             headers={"Authorization": f"Bearer {self.refresh_token}"}) as response:
            if response.status_code != 200:
                print("refresh", response.status_code)
                print("refresh", response.json(), response.status_code)
            else:
                self.token = response.json()['data']['access_token']
                self.refresh_token = response.json()['data']['refresh_token']
                self.user_id = response.json()['data']['id']

    @task(5)
    def get_profile(self):
        with self.client.get(f"/api/v0/users/{self.user_id}/profile",
                             headers={"Authorization": f"Bearer {self.token}"}) as response:
            if response.status_code != 200:
                print("get_profile", response.json(), response.status_code)

    @task(2)
    def update_profile(self):
        with self.client.put(f"/api/v0/users/{self.user_id}/profile",
                             headers={"Authorization": f"Bearer {self.token}"},
                             json={
                                 "first_name": self.first_name,
                                 "last_name": self.last_name,
                                 "birth_date": self.birth_date,
                                 "drinks_alcohol": habits[random.randint(0, len(habits) - 1)],
                                 "family_plans": family_plans[random.randint(0, len(family_plans) - 1)],
                                 "has_children": fake_gen.boolean(),
                                 "height": random.randint(150, 200),
                                 "intention": intentions[random.randint(0, len(intentions) - 1)],
                                 "location": "California",
                                 "preferred_partner": preferences[random.randint(0, len(preferences) - 1)],
                                 "sex": genders[random.randint(0, len(genders) - 1)],
                                 "smokes": habits[random.randint(0, len(habits) - 1)],
                             }) as response:
            if response.status_code != 200:
                print("update_profile", response.json(), response.status_code)

    @task(2)
    def create_prompt(self):
        question = fake_gen.sentence()
        while question in self.allPrompts:
            question = fake_gen.sentence()
        response = self.client.post(f"/api/v0/users/{self.user_id}/prompts/text",
                                    headers={"Authorization": f"Bearer {self.token}"}, json={
                "content": fake_gen.sentence(),
                "question": question,
                "type": "text"
            })
        self.prompt_ids.append(response.json()['data']['id'])

    @task(3)
    def get_prompts(self):
        self.client.get(f"/api/v0/users/{self.user_id}/prompts", headers={"Authorization": f"Bearer {self.token}"})

    @task(5)
    def get_recommendation(self):
        with self.client.get(f"/api/v0/users/{self.user_id}/profile/recommendation",
                             headers={"Authorization": f"Bearer {self.token}"}, catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @task(3)
    def get_full_profile(self):
        self.client.get(f"/api/v0/users/{self.user_id}/profile/full",
                        headers={"Authorization": f"Bearer {self.token}"})

    @task(2)
    def update_prompt(self):
        question = fake_gen.sentence()
        while question in self.allPrompts:
            question = fake_gen.sentence()
        self.client.put(
            f"/api/v0/users/{self.user_id}/prompts/text/{self.prompt_ids[random.randint(0, len(self.prompt_ids) - 1)]}",
            headers={"Authorization": f"Bearer {self.token}"}, json={
                "content": fake_gen.sentence(),
                "question": question,
                "type": "text"
            })

class WebsiteUser(FastHttpUser):
    network_timeout = 120.0
    connection_timeout = 120.0
    tasks = [UserBehavior]
    wait_time = between(0.001, 0.002)