import json
import random

with open('comments.json', 'r') as file:
    comment_data = json.load(file)

comment_list = comment_data["comments"]


print(comment_list[random.randint(0, len(comment_list))])
