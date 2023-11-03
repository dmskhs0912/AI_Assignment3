import hw3, json, time

if __name__ == "__main__":

    with open('./sample.json', 'r') as f:
        data = json.load(f)

    for wid, world in data.items():

        rules = world['rules']
        questions = world['questions']
        rules, variables = hw3.standardize_variables(rules)
        score = 0
        total = 0

        START = time.time()
        hw3.apply({'antecedents':[['x','is','nice',True],['x','is','hungry',False]], 'consequent':['x','eats','squirrel',False]}, 
      [['bobcat','eats','squirrel',False], ['bobcat','visits','squirrel',True], ['bald eagle','eats','squirrel',False]], ['x','y','a','b'])

        for qid, question in questions.items():
            total += 1
            proof = hw3.backward_chain(question['query'], rules, variables)
            if (question['answer'] in (False, 'NAF', 'CWA') and proof is None) or (question['answer'] and proof):
                score += 1

        END = time.time()

        print(f"World({wid}) {score}/{total} passed. ({(END-START):.6f}s elapsed)")

 