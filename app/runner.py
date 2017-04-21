import celery
import docker
import locale
import os
import subprocess
import tempfile


EXECUTOR_IMAGE = 'alvelazq/runner:latest'
INTERNAL_FILE = '/tmp/test.py'

broker = os.environ.get('BROKER')
default_broker = 'pyamqp://' + os.environ.get('MASTER_IP')
backend = os.environ.get('BACKEND')
default_backend = 'redis://' + os.environ.get('MASTER_IP')

app = celery.Celery('runner')
app.conf.broker_url = broker if broker else default_broker
app.conf.result_backend = backend if backend else default_backend

encoding = locale.getdefaultlocale()[1]

def make_temp_file(contents):
    f = tempfile.NamedTemporaryFile(mode='w')
    f.write(contents)
    f.flush()
    return f

@app.task
def run_and_shutdown_worker(task_id, source_code):
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
    container = client.containers.run(image=EXECUTOR_IMAGE,
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
