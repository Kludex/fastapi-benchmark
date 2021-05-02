import itertools
import logging
import os
from time import sleep
from typing import List, TypedDict

import docker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Server(TypedDict):
    name: str
    command: str


def get_daphne_commands() -> List[Server]:
    return [Server(name="daphne", command="daphne -p 8000 -b 0.0.0.0 main:app")]


def get_gunicorn_commands() -> List[Server]:
    return [
        Server(
            name=f"gunicorn {workers}-{threads}",
            command=f"gunicorn -k uvicorn.workers.UvicornWorker -w {workers} --threads {threads} --log-level error main:app -b '0.0.0.0:8000'",
        )
        for workers, threads in itertools.product(range(1, 9), range(1, 9))
    ]


def get_uvicorn_commands() -> List[Server]:
    return [
        Server(
            name=f"uvicorn {workers}",
            command=f"uvicorn --workers {workers} --log-level error main:app --host 0.0.0.0 --port 8000",
        )
        for workers in range(1, 9)
    ]


def get_hypercorn_commands() -> List[Server]:
    return [
        Server(
            name=f"hypercorn {loop}-{workers}",
            command=f"hypercorn -k {loop} -w {workers} --log-level error main:app -b '0.0.0.0:8000'",
        )
        for loop, workers in itertools.product(
            ["asyncio", "uvloop", "trio"], range(1, 9)
        )
    ]


class DockerSetup:
    def __init__(
        self,
        client: docker.DockerClient,
        path: str,
        name: str,
        command: str,
        network: str,
    ):
        self.path = path
        self.name = name
        self.command = command
        self.network = network
        self.client = client

    def __enter__(self):
        logger.info("Running container.")
        self.client.containers.run(
            image=self.name,
            name=self.name,
            detach=True,
            command=self.command,
            network=self.network,
            remove=True,
        )
        return self.client

    def __exit__(self, *exc):
        logger.info("Stopping container.")
        container = self.client.containers.get(self.name)
        container.stop()
        sleep(10)


if __name__ == "__main__":
    servers: List[Server] = itertools.chain(
        get_daphne_commands(),
        get_gunicorn_commands(),
        get_hypercorn_commands(),
        get_uvicorn_commands(),
    )
    network = "data"
    path = os.getcwd()

    client = docker.from_env()
    logger.info("Building image.")
    client.images.build(path=path, nocache=True, tag="app")
    client.networks.create(network)

    for server in servers:
        logger.info("Start benchmark for %s.", server["name"])
        with DockerSetup(
            client=client,
            path=path,
            name="app",
            command=server["command"],
            network=network,
        ) as client:
            logger.info("Running wrk command.")
            client.containers.run(
                "williamyeh/wrk",
                command="-d15s -t4 -c64 http://app:8000/ -s /scripts/script.lua",
                environment={
                    "NAME": server["name"],
                    "FILENAME": "/results/results.csv",
                },
                remove=True,
                network=network,
                volumes={
                    os.path.join(path, "scripts"): {"bind": "/scripts", "mode": "rw"},
                    os.path.join(path, "results"): {"bind": "/results", "mode": "rw"},
                },
            )

# TODO: Add nginx asgi.
