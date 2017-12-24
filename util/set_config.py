import os
import subprocess

def grab_config():
    config = {}
    with open('.env', 'r') as fp:
        lines = fp.readlines()
    for line in lines:
        key, value = line.split('=')
        config[key] = value
    return config

def set_variable(key, value):
    subprocess.call(['heroku', 'config:set', '{}={}'.format(key, value)])

def main():
    config = grab_config()
    for key, val in config.items():
        set_variable(key, val)

if __name__ == '__main__':
    main()