from plugin import MusicSourceSeparatePlugin
from tuneflow_devkit import Runner
from pathlib import Path
from msgpack import packb
from fastapi import Response

store = {}


def upload_result_in_cache(job_id: str, result):
    store[job_id] = result


async_config = {
    "store": {
        "uploader": upload_result_in_cache,
        "resultUrlResolver": lambda job_id: f'http://127.0.0.1:8000/plugin-service/demucs/jobs/{job_id}'
    }
}

app = Runner(plugin_class_list=[MusicSourceSeparatePlugin], bundle_file_path=str(Path(
    __file__).parent.joinpath('bundle.json').absolute())).start(path_prefix='/plugin-service/demucs', config={
        "async": async_config
    })


@app.get('/plugin-service/demucs/jobs/{job_id}')
def handle_get_job_result(job_id: str):
    if job_id not in store:
        return Response('', status_code=404)
    return Response(store[job_id], headers={"Content-Type": "application/octet-stream"})
