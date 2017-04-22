import celery
import docker
import locale
import os
import subprocess
import tempfile


RUNNER_IMAGE = 'alvelazq/runner:latest'
INTERNAL_FILE = '/tmp/test.py'


app = celery.Celery('runner',
                    broker=os.environ['BROKER'],
                    backend=os.environ['BACKEND'])

encoding = locale.getdefaultlocale()[1]

def make_temp_file(contents):
    f = tempfile.NamedTemporaryFile(mode='w')
    f.write(contents)
    f.flush()
    return f

@app.task
def run_and_shutdown(task_id, source_code):
    f = make_temp_file(source_code)
    p = subprocess.Popen(['python3', f.name],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = p.communicate()
    f.close()
    subprocess.call('celery control shutdown'.split())
    return {'task_id': task_id,
            'stdout': stdoutdata.decode(encoding),
            'stderr': stderrdata.decode(encoding)}

@app.task
def run_in_container(task_id, source_code):
    f = make_temp_file(source_code)
    client = docker.from_env()
    volumes = {'/var/run/docker.sock':
                    {'bind': '/var/run/docker.sock', 'mode': 'rw'},
               f.name:
                    {'bind': INTERNAL_FILE, 'mode': 'r'}}
    container = client.containers.run(image=RUNNER_IMAGE,
                                      command=['python3', INTERNAL_FILE],
                                      volumes=volumes,
                                      detach=True,
                                      stdout=True,
                                      stderr=True)
    stdoutdata = container.logs(stdout=True, stderr=False)
    stderrdata = container.logs(stdout=False, stderr=True)
    container.remove()
    f.close()
    return {'task_id': task_id,
            'stdout': stdoutdata.decode(encoding),
            'stderr': stderrdata.decode(encoding)}


run = run_in_container if os.environ.get('STANDALONE') else run_and_shutdown
