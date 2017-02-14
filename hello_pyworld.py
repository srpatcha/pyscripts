import sys
print("I like typing this.")
print("This is fun.")
print('Yay! Printing.')
print("I'd much rather you 'not'.")
print('I "said" do not touch this.')
namonama=sys.platform
print(namonama)
lucky=21
sr1=34
print(lucky, "dergadg",sr1)
print ("So I said, \"You don't know me! You'll never understand me!\"")
print("bouncy, " * 3)
print (len("Hello, world!"))

question = "What did you have for lunch?"
print (question)
answer = input() #You should use "input()" in python 3.x, because python 3.x doesn't have a function named "raw_input".
print("Hello, world!"[3:9])
print ("You had " + answer + "! That sounds delicious!")
print ("Please give me a number to add 10: ")
number = input()
numbee = int(number)
plusTen = numbee + 10
print ("If we add 10 to your number, we get %s" % plusTen)
"Hello, world!"[3:9]
spam = ["bacon", "eggs", 17]
print(len(spam))
definitions = {"guava": "a tropical fruit", "python": "a programming language", "the answer": 42}
print(definitions["the answer"])
d={1:'one',2:'two',3:'three'}
def search(d,v):
    for i in d:
        if d[i]==v:
            return(i)
    return('the value not found')
v1=input('enter a value to be recorded')
print(search(d,v1))

