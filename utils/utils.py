def get_age_postfix(age) -> None:
    k = int(age) % 10
    if k == 1 and (10 > k or k > 20):
        t = "год"
    elif 1 < k < 5 and (10 > k or k > 20):
        t = "года"
    else:
        t = "лет"
    return t