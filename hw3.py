import copy, queue

def standardize_variables(nonstandard_rules): 
    '''
    @param nonstandard_rules (dict) - dict from ruleIDs to rules
        Each rule is a dict:
        rule['antecedents'] contains the rule antecedents (a list of propositions)
        rule['consequent'] contains the rule consequent (a proposition).
   
    @return standardized_rules (dict) - an exact copy of nonstandard_rules,
        except that the antecedents and consequent of every rule have been changed         something을 변수명으로 고친 것 -> standardized_rules. 
        to replace the word "something" with some variable name that is                   변수 명은 유일해야함. 다른 rule에 share되면 안됨.
        unique to the rule, and not shared by any other rule.
    @return variables (list) - a list of the variable names that were created.            생성된 변수명 list. rule에서 사용되는 변수명만 포함.
        This list should contain only the variables that were used in rules.
    '''
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
    '''
    @param query: proposition that you're trying to match.
      The input query should not be modified by this function; consider deepcopy.       query 바뀌면 안됨!! -> deepcopy 사용 고려
    @param datum: proposition against which you're trying to match the query.
      The input datum should not be modified by this function; consider deepcopy.       datum 바뀌면 안됨!! -> deepcopy 사용 고려
    @param variables: list of strings that should be considered variables.
      All other strings should be considered constants.                                 이외의 문자열은 constant로 생각해야함.
    
    Unification succeeds if (1) every variable x in the unified query is replaced by a 
    variable or constant from datum, which we call subs[x], and (2) for any variable y
    in datum that matches to a constant in query, which we call subs[y], then every 
    instance of y in the unified query should be replaced by subs[y].

    @return unification (list): unified query, or None if unification fails.
    @return subs (dict): mapping from variables to values, or None if unification fails.
       If unification is possible, then answer already has all copies of x replaced by
       subs[x], thus the only reason to return subs is to help the calling function
       to update other rules so that they obey the same substitutions.

    Examples:

    unify(['x', 'eats', 'y', False], ['a', 'eats', 'b', False], ['x','y','a','b'])
      unification = [ 'a', 'eats', 'b', False ]
      subs = { "x":"a", "y":"b" }

    unify(['bobcat','eats','y',True],['a','eats','squirrel',True], ['x','y','a','b'])
      unification = ['bobcat','eats','squirrel',True]
      subs = { 'a':'bobcat', 'y':'squirrel' }

    unify(['x','eats','x',True],['a','eats','a',True],['x','y','a','b'])
      unification = ['a','eats','a',True]
      subs = { 'x':'a' }

    unify(['x','eats','x',True],['a','eats','bobcat',True],['x','y','a','b'])
      unification = ['bobcat','eats','bobcat',True],
      subs = {'x':'a', 'a':'bobcat'}
      When the 'x':'a' substitution is detected, the query is changed to 
      ['a','eats','a',True].  Then, later, when the 'a':'bobcat' substitution is 
      detected, the query is changed to ['bobcat','eats','bobcat',True], which 
      is the value returned as the answer.

    unify(['a','eats','bobcat',True],['x','eats','x',True],['x','y','a','b'])
      unification = ['bobcat','eats','bobcat',True],
      subs = {'a':'x', 'x':'bobcat'}
      When the 'a':'x' substitution is detected, the query is changed to 
      ['x','eats','bobcat',True].  Then, later, when the 'x':'bobcat' substitution 
      is detected, the query is changed to ['bobcat','eats','bobcat',True], which is 
      the value returned as the answer.

    unify([...,True],[...,False],[...]) should always return None, None, regardless of the 
      rest of the contents of the query or datum.
    '''
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

def apply(rule, goals, variables):
    '''
    @param rule: A rule that is being tested to see if it can be applied
      This function should not modify rule; consider deepcopy.
    @param goals: A list of propositions against which the rule's consequent will be tested
      This function should not modify goals; consider deepcopy.
    @param variables: list of strings that should be treated as variables

    Rule application succeeds if the rule's consequent can be unified with any one of the goals.    rule의 결론이 goal중의 하나로 unify 될 수 있는가?
    
    @return applications: a list, possibly empty, of the rule applications that
       are possible against the present set of goals.
       Each rule application is a copy of the rule, but with both the antecedents          변수 치환으로 unify한 상태. 전제 -> 결론
       and the consequent modified using the variable substitutions that were
       necessary to unify it to one of the goals. Note that this might require 
       multiple sequential substitutions, e.g., converting ('x','eats','squirrel',False)
       based on subs=={'x':'a', 'a':'bobcat'} yields ('bobcat','eats','squirrel',False).
       The length of the applications list is 0 <= len(applications) <= len(goals).  
       If every one of the goals can be unified with the rule consequent, then 
       len(applications)==len(goals); if none of them can, then len(applications)=0.
    @return goalsets: a list of lists of new goals, where len(newgoals)==len(applications).
       goalsets[i] is a copy of goals (a list) in which the goal that unified with 
       applications[i]['consequent'] has been removed, and replaced by 
       the members of applications[i]['antecedents'].

    Example:
    rule={
      'antecedents':[['x','is','nice',True],['x','is','hungry',False]],
      'consequent':['x','eats','squirrel',False]
    }
    goals=[
      ['bobcat','eats','squirrel',False],
      ['bobcat','visits','squirrel',True],
      ['bald eagle','eats','squirrel',False]
    ]
    variables=['x','y','a','b']

    applications, newgoals = submitted.apply(rule, goals, variables)

    applications==[
      {
        'antecedents':[['bobcat','is','nice',True],['bobcat','is','hungry',False]],
        'consequent':['bobcat','eats','squirrel',False]
      },
      {
        'antecedents':[['bald eagle','is','nice',True],['bald eagle','is','hungry',False]],
        'consequent':['bald eagle','eats','squirrel',False]
      }
    ]
    newgoals==[
      [
        ['bobcat','visits','squirrel',True],
        ['bald eagle','eats','squirrel',False]
        ['bobcat','is','nice',True],
        ['bobcat','is','hungry',False]
      ],[
        ['bobcat','eats','squirrel',False]
        ['bobcat','visits','squirrel',True],
        ['bald eagle','is','nice',True],
        ['bald eagle','is','hungry',False]
      ]
    '''
    raise RuntimeError("You need to write this part!")
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
    raise RuntimeError("You need to write this part!")
    return proof
