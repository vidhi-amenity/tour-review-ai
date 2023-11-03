import os
import environ

def make_env():
    root = os.path.join(os.path.dirname(__file__), os.pardir)
    env = environ.Env(
        ENV_NAME=(str, 'production'),
        DEBUG=(bool, False))
    environ.Env.read_env(env_file=os.path.join(root, '.env'))
    return env

env = make_env()
