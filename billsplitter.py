# write your code here
import random

friends = {}

msg_0 = "Enter the number of friends joining (including you):"
msg_1 = "Enter the name of every friend (including you), each on a new line:"
msg_2 = "Enter the total bill value:"
msg_3 = "Do you want to use the \"Who is lucky?\" feature? Write Yes/No:"

friend_number = int(input(msg_0))
print()


def lucky_feature():
    answer = input(msg_3)
    assert answer == "Yes"
    lucky_name = random.choice(list(friends.keys()))
    return lucky_name


if friend_number <= 0:
    print("No one is joining for the party")
else:
    print(msg_1)
    for i in range(friend_number):
        friends[input()] = 0
    print()
    bill_value = int(input(msg_2))
    print()
    name = ""
    try:
        name = lucky_feature()
        print()
        print("{} is the lucky one!".format(name))
    except AssertionError:
        print()
        print("No one is going to be lucky")
    if name == "":
        split_value = round(bill_value / friend_number, 2)
        for key, value in friends.items():
            friends[key] = split_value
    else:
        split_value = round(bill_value/(friend_number - 1), 2)
        for key, value in friends.items():
            if key == name:
                friends[key] = 0
            else:
                friends[key] = split_value
    print(friends)
