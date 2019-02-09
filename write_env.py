import os


if __name__ == '__main__':
    with open('.envasdf', 'w+') as env_file:
        for k, v in os.environ.items():
            print(k)
            if k.startswith('AZURE') or k.startswith('COSMOS') or k.startswith('ACCOUNT'):
                env_file.write(k + '=' + v + '\n')
