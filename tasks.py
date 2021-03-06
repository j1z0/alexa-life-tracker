# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
from invoke.exceptions import UnexpectedExit
from contextlib import contextmanager
from invoke import task, run
import cProfile
import pstats
import importlib
import requests
import random
import aws_lambda


docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_NAME = 'life_tracker'
POSITIVE = 'https://gist.github.com/j1z0/bbed486d85fb4d64825065afbfb2e98f/raw/positive.txt'
NEGATIVE = 'https://gist.github.com/j1z0/bbed486d85fb4d64825065afbfb2e98f/raw/negative.txt'


def get_random_line_in_gist(url):
    listing = requests.get(url)
    return random.choice(listing.text.split("\n"))


@task
def play(ctx, positive=False):
    type_url = POSITIVE if positive else NEGATIVE
    # no spaces in url
    media_url = '%20'.join(get_random_line_in_gist(type_url).split())
    run("vlc -I rc %s --play-and-exit -q" % (media_url))


@contextmanager
def setenv(**kwargs):
    # Backup
    prev = {}
    for k, v in kwargs.items():
        if k in os.environ:
            prev[k] = os.environ[k]
        os.environ[k] = v

    yield

    # Restore
    for k in kwargs.keys():
        if k in prev:
            os.environ[k] = prev[k]
        else:
            del os.environ[k]


@task(aliases=['notebooks'])
def notebook(ctx):
    """
    Start IPython notebook server.
    """
    with setenv(PYTHONPATH='{root}/{prj}:{root}:{root}/tests'.format(root=ROOT_DIR, prj=PROJECT_NAME),
                JUPYTER_CONFIG_DIR='{root}/notebooks'.format(root=ROOT_DIR)):

        os.chdir('notebooks')

        # Need pty=True to let Ctrl-C kill the notebook server. Shrugs.
        try:
            run('jupyter nbextension enable --py widgetsnbextension')
            run('jupyter notebook --ip=*', pty=True)
        except KeyboardInterrupt:
            pass
        print("If notebook does not open on your chorme automagically, try adding this to your bash_profie")
        print("export BROWSER=/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome")
        print("*for MacOS and Chrome only")


@task()
def share_notebook(ctx, branch='master'):
    # get git repo called origin
    print("sharing from github repo, NOT local")
    repo = run('git remote get-url origin').stdout.strip('\n')
    if not repo.startswith("http"):
        # ssh like git@github.com:org/name
        repo = repo.split(':')[-1]

    org, name = repo.split('/')[-2:]

    # https://mybinder.org/v2/gh/hms-dbmi/pystarter.git/master
    url = "https://mybinder.org/v2/gh/%s/%s/%s?filepath=notebooks" % (org, name, branch)
    print("Notebook can be accessed from here %s" % url)
    webbrowser.open_new_tab(url)


@task
def loc(ctx):
    """
    Count lines-of-code.
    """
    excludes = ['/test/', 'docs', 'htmlcov', 'README.md', 'README.rst', '.eggs']

    run('find . -iname "*py" | grep -v {} | xargs wc -l | sort -n'.format(
        ' '.join('-e ' + e for e in excludes)))


@task(aliases=['tests'])
def test(ctx, watch=False, last_failing=False, no_flake=False, k=''):
    """Run the tests.
    Note: --watch requires pytest-xdist to be installed.
    """
    import pytest
    if not no_flake:
        flake(ctx)
    args = []
    if k:
        args.append('-k %s' % k)
    if watch:
        args.append('-f')
    if last_failing:
        args.append('--lf')
    retcode = pytest.main(args)
    try:
        good = True if retcode == 0 else False
        play(ctx, good)
    except:  # noqa E722
        print("install vlc for more exciting test runs...")
        pass
    if retcode != 0:
        print("test failed exiting")
        sys.exit(retcode)
    return retcode


@task
def create_user(ctx, amz_user_id=None, habitica_user=None, habitica_key=None):
    if amz_user_id is None:
        amz_user_id = os.environ.get("AMZ_USER_ID")
    if habitica_user is None:
        habitica_user = os.environ.get("HABITICA_USER")
    if habitica_key is None:
        habitica_key = os.environ.get("HABITICA_TOKEN")
    from nodb import NoDB
    nodb = NoDB()
    nodb.serializer = "json"
    nodb.bucket = 'alexa-life-tracker'
    nodb.index = 'user'
    # check if exists first
    nodb_key = amz_user_id + '-keys'
    lt_user = nodb.load(nodb_key)
    if not lt_user:
        print("user not found, creating new entry")
        lt_user = {}
    else:
        print('user found data is %s ' % str(lt_user))

    print("updating user")
    lt_user.update({'user': nodb_key,
                    'habitica_user': habitica_user,
                    'habitica_key': habitica_key
                    })
    nodb.save(lt_user)


@task
def flake(ctx):
    '''static linter to ensure code passes standards'''
    """Run flake8 on codebase."""
    run('flake8 .', echo=True)
    print("flake8 passed!!!")


@task
def clean(ctx):
    '''remove temporary build stuff'''
    run("rm -rf build")
    run("rm -rf dist")
    run("rm -rf *.egg-info")
    clean_docs(ctx)
    print("Cleaned up.")


@contextmanager
def chdir(dirname=None):
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
            yield
    finally:
        os.chdir(curdir)


@task
def deploy(ctx, version=None, no_tests=False, no_flake=False, name=u'life_tracker'):
    print("preparing for deploy...")
    print("make sure tests pass")
    if no_tests is False:
        if test(ctx, no_flake=no_flake) != 0:
            print("tests need to pass first before deploy")
            return

    # dist directores are the enemy, clean the all
    print("cleaning house before deploying")
    with chdir("./lambdas/%s/" % name):
        clean(ctx)

        print("building lambda package")
        deploy_lambda_package(ctx, name)
        # need to clean up all dist, otherwise, installing local package takes forever
        clean(ctx)


@task
def deploy_lambda_package(ctx, name):
    # third part tools, should all be tar
    '''
    tools_dir = os.path.join(ROOT_DIR, "third_party")
    bin_dir = os.path.join(ROOT_DIR, "bin")

    for filename in os.listdir(tools_dir):
        if filename.endswith('.tar'):
            fullpath = os.path.join(tools_dir, filename)
            run("tar -xvf %s -C %s" % (fullpath, bin_dir))
    '''
    aws_lambda.deploy(os.getcwd(), requirements='../../requirements.txt')


@task
def update_version(ctx, version=None):
    '''update version of your library to be used in pypi'''
    import importlib
    vmod = importlib.import_module('%s._version' % PROJECT_NAME)
    print("Current version is ", vmod.__version__)
    if version is None:
        msg = "What version would you like to set for new release (please use x.x.x / semantic versioning): "
        if sys.version_info < (3, 0):
            version = raw_input(msg)  # noqa: F821
        else:
            version = input(msg)

    # read the versions file
    lines = []
    with open(PROJECT_NAME + "/_version.py") as readfile:
        lines = readfile.readlines()

    if lines:
        with open(PROJECT_NAME + "/_version.py", 'w') as writefile:
            lines[-1] = '__version__ = "%s"\n' % (version.strip())
            writefile.writelines(lines)

    run("git add %s/_version.py" % PROJECT_NAME)
    run("git commit -m 'version bump'")
    print("version updated to", version)
    return version


@task
def git_tag(ctx, tag_name, msg):
    """create a tag and push to github.  Will trigger pypi publish if travis is setup"""
    run('git tag -a %s -m "%s"' % (tag_name, msg))
    run('git push --tags')
    run('git push')


@task
def clean_docs(ctx):
    """clean all generated docs"""
    run("rm -rf %s" % build_dir, echo=True)


@task
def browse_docs(ctx):
    """show the generated docs in a webbrowser"""
    path = os.path.join(build_dir, 'index.html')
    webbrowser.open_new_tab(path)


@task
def docs(ctx, clean=False, browse=False, watch=False):
    """Build the docs."""
    if clean:
        clean_docs(ctx)
    run("sphinx-build %s %s" % (docs_dir, build_dir), echo=True)
    if browse:
        browse_docs(ctx)
    if watch:
        watch_docs(ctx)


@task
def watch_docs(ctx):
    """Run build the docs when a file changes."""
    try:
        import sphinx_autobuild  # noqa
    except ImportError:
        print('ERROR: watch task requires the sphinx_autobuild package.')
        print('Install it with:')
        print('    pip install sphinx-autobuild')
        sys.exit(1)
    run('sphinx-autobuild {0} {1} --watch {2}'.format(
        docs_dir, build_dir, '4DNWranglerTools'), echo=True, pty=True)


@task
def browse_cov(ctx, norun=False):
    '''View test coverage results in browser'''
    if not norun:
        try:
            test(ctx)
        except UnexpectedExit:
            pass
    webbrowser.open_new_tab('htmlcov/index.html')


@task
def publish(ctx, test=False):
    """Publish to the cheeseshop."""
    clean(ctx)
    if test:
        run('python setup.py register -r test sdist bdist_wheel', echo=True)
        run('twine upload dist/* -r test', echo=True)
    else:
        run('python setup.py register sdist bdist_wheel', echo=True)
        run('twine upload dist/*', echo=True)


@task
def profile(ctx, module, method, filename=None):
    '''
    run modeule.method through the profile and dump results to filename
    '''

    mod = importlib.import_module(module)
    fn = getattr(mod, method)
    pr = cProfile.Profile()
    pr.enable()
    res = fn()
    pr.disable()
    if res:
        print(res)
    pr.create_stats()
    ps = pstats.Stats(pr).sort_stats('time')
    ps.print_stats()
    ps.print_callers()
    ps.print_callees()
    if filename is not None:
        ps.dump_stats(filename)
