from django import template


register = template.Library()


censored_word = ["Редиска", "редиска"]

@register.filter()
def censor(value):
    for word in censored_word:
        if word.lower() in value.lower():
            value = value.replace(word[1:], '*' * len(word))
    return value
