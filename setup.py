from setuptools import setup

def get_git_version():
    """
    Use git describe to get version based on git tag.
    """
    from subprocess import check_output
    output = check_output(['git', 'describe', '--dirty',]).decode()
    version = output[:-1] # had trailing newline
    return version

setup(name='utils',
      version=get_git_version(),
      description='Utils',
      author='Achim Randelhoff',
      packages=['utils',],
      install_requires=[
      ],
     )
