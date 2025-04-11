import random
import string

brainrot = ["skibidi", "toilet", "rizz", "brainrot", "gyatt", "ohio", "tax", "gooner", "comp"]
names = ["zentrr", "arctic", "rodrigo", "gonzalez"]
triggers = ["pedo", "minor", "racist", "hard r"]
char = ["o", "j", "0", "x", "1", "l", "9"]
char2 = ["y", "F", "0", "a", "g", "9", "6"]

def create_name():
    return random.choice(brainrot) + random.choice(names) + random.choice(triggers)

def create_password():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))