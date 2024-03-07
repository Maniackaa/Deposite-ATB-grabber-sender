devices = ['111', '2', '222']
serials = ['111', '222']
names = ['1nmae', '2name']

for device in devices:
    print(device)
    if device in serials:
        index = serials.index(device)
        print('name', names[index])