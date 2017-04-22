import celery
import locale
import os
import subprocess
import sys
import tempfile


RUNNER_IMAGE = 'python' # Must have python3 in path
INTERNAL_FILE = '/tmp/test.py'


if not os.environ.get('BROKER') or not os.environ.get('BACKEND'):
    sys.stderr.write('Error: you must set both $BROKER and $BACKEND\n')
    sys.exit(1)

containerize = bool(os.environ.get('CONTAINERIZE'))

if containerize:
    try:
        import docker
    except:
        sys.stderr.write('Docker library not found\n')
        sys.exit(2)
    client = docker.from_env()

encoding = locale.getdefaultlocale()[1]

app = celery.Celery('runner',
                    broker=os.environ['BROKER'],
                    backend=os.environ['BACKEND'])


def make_temp_file(contents):
    f = tempfile.NamedTemporaryFile(mode='w', dir='/tmp')
    f.write(contents)
    f.flush()
    return f

def run_and_shutdown(task_id, source_code):
    f = make_temp_file(source_code)
    p = subprocess.Popen(['python3', f.name],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = p.communicate()
    f.close()
    subprocess.call('celery control shutdown'.split())
    return {'task_id': task_id, 'stdout': stdoutdata.decode(encoding)}

def run_in_container(task_id, source_code):
    f = make_temp_file(source_code)
    volumes = {f.name: {'bind': INTERNAL_FILE, 'mode': 'ro'}}
    logs = client.containers.run(image=RUNNER_IMAGE,
                                 command=['python3', INTERNAL_FILE],
                                 volumes=volumes,
                                 remove=True)
    f.close()
    return {'task_id': task_id, 'stdout': logs.decode(encoding)}


@app.task
def run(task_id, source_code):
    if containerize:
        return run_in_container(task_id, source_code)
    else:
        return run_and_shutdown(task_id, source_code)
