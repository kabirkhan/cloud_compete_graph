import os


if __name__ == '__main__':
    with open('.env', 'w+') as env_file:
        for k, v in os.environ.items():
            if k.startswith('AZURE') or k.startswith('COSMOS') or k.startswith('ACCOUNT'):
                print(k)
                env_file.write(k + '=' + v + '\n')
