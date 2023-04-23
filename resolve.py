
def move(array):
    n = len(array)
    while n > 1 and array[n - 1][0] < array[n - 2][0]:
        array[n - 1], array[n - 2] = array[n - 2], array[n - 1]
        n -= 1


def resolve(group):
    debt_array = group.debts
    if len(debt_array) == 0:
        return
    n = len(group.id_lib)

    vertices = {}
    cnt = 0
    for i in group.id_lib:
        vertices.update([(group.id_lib[i], cnt)])
        cnt += 1

    graph = [[0 for i in range(n)] for j in range(n)]
    for debt in debt_array:
        print(debt_to_text(debt, group_id))
        payer = debt.payer
        sum_val = debt.sum / len(debt.debtors)
        for debtor in debt.debtors:
            if not debtor == payer:
                graph[vertices[debtor]][vertices[payer]] += sum_val
        print(graph)

    personal_total = {pers: 0 for pers in group.id_lib.values()}
    for pers in personal_total:
        for i in range(n):
            personal_total[pers] += (graph[i][vertices[pers]]
                                     - graph[vertices[pers]][i])
    print(personal_total)

    plus_money = []
    minus_money = []
    all_set = []

    for pers in personal_total:
        if personal_total[pers] > 0:
            plus_money.append((personal_total[pers], pers))
        elif personal_total[pers] < 0:
            minus_money.append((-personal_total[pers], pers))
        else:
            all_set.append(pers)

    plus_money.sort()
    minus_money.sort()

    i = 0
    j = 0
    n = len(plus_money) - 1
    m = len(minus_money) - 1
    solution = []
    while i <= n and j <= m:
        if plus_money[i][0] < minus_money[j][0]:
            i += 1
        elif plus_money[i][0] > minus_money[j][0]:
            j += 1
        else:
            solution.append((minus_money[j][1], plus_money[i][1], plus_money[i][0]))
            del plus_money[i]
            del minus_money[j]
            n -= 1
            m -= 1
    print(n, m, len(plus_money), len(minus_money))

    while n >= 0:
        while m >= 0 and plus_money[n][0] >= minus_money[m][0]:
            solution.append((minus_money[m][1], plus_money[n][1], minus_money[m][0]))
            plus_money[n] = (plus_money[n][0] - minus_money[m][0], plus_money[n][1])
            # plus_money[n][0] -= minus_money[m][0]
            del minus_money[m]
            m -= 1
            if plus_money[n][0] < 0.25:
                del plus_money[n]
                n -= 1
        if n > 0 and plus_money[n - 1][0] > minus_money[m][0]:
            move(plus_money)
        elif n >= 0 and m >= 0:
            solution.append((minus_money[m][1], plus_money[n][1], plus_money[n][0]))
            minus_money[m] = (minus_money[m][0] - plus_money[n][0], minus_money[m][1])
            # minus_money[m][0] -= plus_money[n][0]
            del plus_money[n]
            n -= 1

