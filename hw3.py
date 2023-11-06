import copy, queue

def standardize_variables(nonstandard_rules): 
    standardized_rules = copy.deepcopy(nonstandard_rules) # deepcopy를 이용해 rules 복사
    variables = []
    numVar = 0 # 변수 명 뒤에 붙을 수
    flag = False
    for key, rule in standardized_rules.items() : # 각 rule에 대해 반복.
        for antecedent in rule['antecedents'] : # 각 antecedent에 대해 반복
            for i, value in enumerate(antecedent) :
                if value == "something" or value == "someone" : # something/someone이 있으면 x0001과 같은 변수명으로 교체. 
                    flag = True
                    antecedent[i] = "x" + f"{numVar:04}" # f-string을 사용해 문자열 포맷팅. 뒤에 숫자를 4자리로 고정. 빈 자리는 0으로 채우기.
        for i, value in enumerate(rule['consequent']) : # consequent에 대해서도 변수명 교체
            if value == "something" or value == "someone" :
                flag = True
                rule['consequent'][i] = "x" + f"{numVar:04}"
        if flag is True : # 교체가 이루어졌다면 numVar 증가
            numVar += 1
            flag = False
    
    for i in range(numVar) : # 변수의 수만큼 variables에 변수명 추가
        if numVar == 0 : break
        variables.append("x"+f"{i:04}")
    
    return standardized_rules, variables

def unify(query, datum, variables):
    copied_query = copy.deepcopy(query)
    copied_datum = copy.deepcopy(datum)
    subs = {}
    if len(query) != len(datum) : return None, None # 길이가 다르면 unify 불가.
    if query[-1] != query[-1] : return None, None # True, False 간의 unify는 불가.


    while True : # unify_flag가 false가 되면 while문 탈출. for문에서 아무 내용도 바뀌지 않으면 unify_flag가 false가 됨.
        unify_flag = False
        for q, d in zip(copied_query, copied_datum) : # query와 datum의 각 원소끼리 묶어 비교
            if q != d and q not in variables and d not in variables : return None, None # constant가 서로 다른 경우 unify 불가.
            elif q != d and q in variables and d not in variables :  # q가 변수, d가 상수 인 경우
                unify_flag = True
                subs[q] = d
                for i, value in enumerate(copied_query) :
                    if value == q : copied_query[i] = d
                break
            elif q != d and q not in variables and d in variables : # q가 상수, d가 변수 인 경우
                unify_flag = True
                subs[d] = q
                for i, value in enumerate(copied_datum) :
                    if value == d : copied_datum[i] = q
                break
            elif q != d and q in variables and d in variables : # q와 d 모두 변수인 경우 query를 datum에 맞춤
                unify_flag = True
                subs[q] = d
                for i, value in enumerate(copied_query) :
                    if value == q : copied_query[i] = d
                break
        if not unify_flag : break

    unification = copied_query
    return unification, subs


def substitution(proposition, subs) :
    copied_prop = copy.deepcopy(proposition) # deepcopy 사용해 원본 수정 방지
    for var1, var2 in subs.items() : 
        for i in range(3) :
            if var1 == copied_prop[i] : # subs 딕셔너리의 key와 같은 변수를 찾은 경우 치환 적용
                copied_prop[i] = subs[var1]
    return copied_prop
        
        

def apply(rule, goals, variables):
    copied_rule = copy.deepcopy(rule) # deepcopy 사용으로 원본 수정 방지
    copied_goals = copy.deepcopy(goals)
    applications = []
    goalsets = []
    i = 0 # 적용되는 goal에 대해 application index 처리를 위한 변수 

    for goal in copied_goals : # goals의 각 goal에 대해 적용 가능한지 확인 
        unification, subs = unify(copied_rule['consequent'], goal, variables) # rule의 consequent와 goal이 unify 가능 --> apply 가능.
        if unification is not None : # None이 아닌 경우라면 적용 가능.
            applications.append({'antecedents':[], 'consequent':None})
            applications[i]['consequent'] = unification  # goal과도 동일하다.
            goalsets.append(copy.deepcopy(goals))  # 뒤에 remove 메소드 사용으로 인해 goals가 수정될 수 있으므로 deepcopy 사용.
            goalsets[i].remove(goal)  # apply된 goal은 new goal set에서 제외하고 antecedent를 넣는다. 
            for ante in copied_rule['antecedents'] :
                sub_ante = substitution(ante, subs)  # unify될 때 적용된 치환을 antecedent에도 적용 후 goalsets에 추가.
                applications[i]['antecedents'].append(sub_ante)
                goalsets[i].append(sub_ante)
            i += 1
    return applications, goalsets


def backward_chain(query, rules, variables):
    goal_stack = [query] # 목표 추적을 위한 스택
    proof = []

    while goal_stack: # 스택이 비어있지 않은 동안 반복
        current_goal = goal_stack.pop() # goal을 하나 pop해서 해당 goal에 규칙들을 적용해본다.

        applicable = False
        for rule_id, rule in rules.items():
            applications, newgoalsets = apply(rule, [current_goal], variables)
            if applications: # applications 리스트가 비어있지 않은 경우는 적용 가능한 경우
                applicable = True
                proof.append(applications[0]) # 적용된 rule을 proof로 추가함
                for antecedent in applications[0]['antecedents']: # 적용된 rule의 antecedent를 goal stack에 추가해서 backward_chain을 구현
                    goal_stack.append(antecedent)
                break

        if not applicable: # 만약 현재 목표에 대해 적용할 수 있는 rule이 없다면 증명할 수 없다. 
            return None  

    return proof
