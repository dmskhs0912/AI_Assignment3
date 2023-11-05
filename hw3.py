import copy, queue

def standardize_variables(nonstandard_rules): 
    standardized_rules = copy.deepcopy(nonstandard_rules) # deepcopy를 이용해 rules 복사
    variables = []
    numVar = 0 # 변수 명 뒤에 붙을 수
    for key, rule in standardized_rules.items() : # 각 rule에 대해 반복.
        for antecedent in rule['antecedents'] : # 각 antecedent에 대해 반복
            for i, value in enumerate(antecedent) :
                if value == "something" or value == "someone" : # something/someone이 있으면 x0001과 같은 변수명으로 교체. 
                    numVar += 1
                    antecedent[i] = "x" + f"{numVar:04}" # f-string을 사용해 문자열 포맷팅. 뒤에 숫자를 4자리로 고정. 빈 자리는 0으로 채우기.
        for i, value in enumerate(rule['consequent']) : # consequent에 대해서도 변수명 교체
            if value == "something" or value == "someone" :
                numVar += 1
                rule['consequent'][i] = "x" + f"{numVar:04}"
    
    for i in range(numVar) :
        if numVar == 0 : break
        if i == 0 : continue
        variables.append("x"+f"{i:04}")
    
    #print(standardized_rules, variables)
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
    #print(unification)
    return unification, subs


def substitution(proposition, subs) :
    copied_prop = copy.deepcopy(proposition)
    for var1, var2 in subs.items() :
        for i in range(3) :
            if var1 == copied_prop[i] :
                copied_prop[i] = subs[var1]
    return copied_prop
        
        

def apply(rule, goals, variables):
    copied_rule = copy.deepcopy(rule)
    copied_goals = copy.deepcopy(goals)
    applications = []
    goalsets = []
    i = 0

    for goal in copied_goals :
        unification, subs = unify(copied_rule['consequent'], goal, variables)
        if unification is not None :
            applications.append({'antecedents':[], 'consequent':None})
            applications[i]['consequent'] = unification
            goalsets.append(copy.deepcopy(goals))
            goalsets[i].remove(goal)
            for ante in copied_rule['antecedents'] :
                sub_ante = substitution(ante, subs)
                applications[i]['antecedents'].append(sub_ante)
                goalsets[i].append(sub_ante)
            i += 1
    return applications, goalsets

def backward_chain(query, rules, variables):
    '''
    @param query: a proposition, you want to know if it is true
    @param rules: dict mapping from ruleIDs to rules
    @param variables: list of strings that should be treated as variables

    @return proof (list): a list of rule applications
      that, when read in sequence, conclude by proving the truth of the query.
      If no proof of the query was found, you should return proof=None.
    '''
    goalset_stack = [[query]]
    
    while len(goalset_stack) != 0 : 
        goalset = goalset_stack.pop()
        for rid, rule in rules :
            application, newgoalset = apply(rule, goalset, variables)
            if len(application) == 0 : continue
            else :
                for goals in newgoalset :
                    
                