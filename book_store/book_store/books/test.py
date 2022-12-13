import yadisk
y = yadisk.YaDisk(token="y0_AgAAAAA80jYJAAjfvQAAAADWo2ShwEEwbZRLRSe_ys_viVgBVK-U4Mg")
a = '/'
b = y.get_meta('4прак1.pdf')
print(b['public_url'])
def publik(file):
    # import yadisk
    # y = yadisk.YaDisk(token="y0_AgAAAAA80jYJAAjfvQAAAADWo2ShwEEwbZRLRSe_ys_viVgBVK-U4Mg")
    # a = '/'
    # b = list(y.listdir(a))
    # public_key = 0

    # for i in b:
    #     i = i.__dict__['FIELDS']
    #     if i['name'] == file:
    #         public_key= i['public_url']
    a = y.get_meta(f'/{file.name}')
    public_key = a['public_url']
    return public_key

# print(publik('4прак1.pdf'))
