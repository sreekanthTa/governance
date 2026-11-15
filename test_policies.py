import yaml

with open("policies.yaml") as file:
    config = yaml.safe_load(file)


def check_policy(action):
    for policy in config["policies"]:
        if policy["action"] == action:
            return policy["effect"]

    return "deny"


# Test different actions
test_actions = [
    "chat",
    "read_note",
    "delete_note",
    "send_email",
    "access_payment"
]

for action in test_actions:
    decision = check_policy(action)
    print(f"Action: {action:15} Decision: {decision}")