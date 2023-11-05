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

import copy

def backward_chain(query, rules, variables, proof=None):
    if proof is None:
        proof = []

    # Check if the query is already proved by the given facts (base rules with no antecedents)
    for rule_id, rule in rules.items():
        if not rule['antecedents'] and rule['consequent'] == query:  # it's a fact
            proof.append(rule)
            return proof
                

    # Try to apply rules to prove the query
    for rule_id, rule in rules.items():
        applications, goalsets = apply(rule, [query], variables)
        
        for application, new_goals in zip(applications, goalsets):
            # If there are no more goals to prove, we've found a proof
            if not new_goals:
                proof.append(application)
                return proof
            
            # If there are still goals left, we need to prove each of them
            for new_goal in new_goals:
                subproof = backward_chain(new_goal, rules, variables, proof)
                if subproof is not None:  # if a subproof is found
                    proof.append(application)
                    return proof
    
    # If no proof is found for the query
    return None



'''
def backward_chain(query, rules, variables):
    # 기본 사례: query가 비어 있거나 None이면, 증명이 없음 (query가 이미 참이거나 주어진 query가 없음).
    if not query:
        return []

    # 목표를 추적하기 위해 스택을 초기화합니다 (LIFO).
    goal_stack = [query]
    # 규칙 적용 순서를 수집하기 위한 리스트를 초기화합니다.
    proof = []

    # 처리할 목표가 있을 동안.
    while goal_stack:
        # 스택에서 목표를 하나 꺼냅니다.
        current_goal = goal_stack.pop()

        # 현재 목표에 규칙을 적용해 봅니다.
        applicable = False
        for rule_id, rule in rules.items():
            applications, newgoalsets = apply(rule, [current_goal], variables)

            # 규칙이 적용될 수 있다면, 첫 번째 적용 사례를 선택합니다 (간단함을 위해).
            if applications:
                applicable = True
                # 현재 적용 가능한 규칙으로 증명 순서가 추가됩니다.
                proof.append(applications[0])
                # 새로운 하위 목표로 규칙의 선행조건을 스택에 추가합니다.
                for antecedent in applications[0]['antecedents']:
                    goal_stack.append(antecedent)
                # 첫 번째 적용 가능한 규칙이 찾아지고 적용된 후에 중단합니다.
                break

        # 적용 가능한 규칙을 찾지 못하면, 현재 목표를 증명할 수 없습니다.
        if not applicable:
            return None  # 증명 실패.

    # 모든 목표가 처리되었고 스택이 비어 있으면, 수집된 증명을 반환합니다.
    return proof
'''







    
