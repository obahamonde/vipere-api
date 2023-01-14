from aiodocker import Docker
from kubernetes.schemas.schemas import DataStoreSchema


class DockerService(DataStoreSchema):
    """Docker Service"""

    async def run(self):
        async with Docker() as docker:
            if self.image == "postgres":
                self.container_port = 5432
                self.database_uri = f"postgresql://{self.username}:{self.password}@{self.host}:{self.host_port}/{self.database}"
                container = await docker.containers.create_or_replace(
                    config={
                        "Image": self.image,
                        "Env": [
                            f"POSTGRES_USER={self.username}",
                            f"POSTGRES_PASSWORD={self.password}",
                            f"POSTGRES_DB={self.database}",
                        ],
                        "ExposedPorts": {f"{self.container_port}/tcp": {}},
                        "HostConfig": {
                            "PortBindings": {
                                f"{self.container_port}/tcp": [
                                    {"HostPort": str(self.host_port)}
                                ]
                            }
                        },
                    },
                    name=self.name,
                )
            elif self.image == "mysql":
                self.container_port = 3306
                self.database_uri = f"mysql://{self.username}:{self.password}@{self.host}:{self.host_port}/{self.database}"
                container = await docker.containers.create_or_replace(
                    config={
                        "Image": self.image,
                        "Env": [
                            f"MYSQL_ROOT_PASSWORD={self.password}",
                            f"MYSQL_DATABASE={self.database}",
                        ],
                        "ExposedPorts": {f"{self.container_port}/tcp": {}},
                        "HostConfig": {
                            "PortBindings": {
                                f"{self.container_port}/tcp": [
                                    {"HostPort": str(self.host_port)}
                                ]
                            }
                        },
                    },
                    name=self.name,
                )
            elif self.image == "mongo":
                self.container_port = 27017
                self.database_uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.host_port}/{self.database}"
                container = await docker.containers.create_or_replace(
                    config={
                        "Image": self.image,
                        "Env": [
                            f"MONGO_INITDB_ROOT_USERNAME={self.username}",
                            f"MONGO_INITDB_ROOT_PASSWORD={self.password}",
                            f"MONGO_INITDB_DATABASE={self.database}",
                        ],
                        "ExposedPorts": {f"{self.container_port}/tcp": {}},
                        "HostConfig": {
                            "PortBindings": {
                                f"{self.container_port}/tcp": [
                                    {"HostPort": str(self.host_port)}
                                ]
                            }
                        },
                    },
                    name=self.name,
                )
            else:
                raise Exception("Invalid image")
            await container.start()
            self.container_id = container.id
            return self

    @classmethod
    async def get(cls, name):
        async with Docker() as docker:
            container = await docker.containers.get(name)
            return container.__dict__["_container"]

    @classmethod
    async def list(cls):
        async with Docker() as docker:
            containers = await docker.containers.list()
            response = [container.__dict__["_container"] for container in containers]
            images = [container["Image"] for container in response]
            id = [container["Id"] for container in response]
            name = [container["Names"][0][1:] for container in response]
            ports = [container["Ports"][0] for container in response]
            return [
                {"image": image, "id": id, "name": name, "ports": ports}
                for image, id, name, ports in zip(images, id, name, ports)
            ]

    @classmethod
    async def delete(cls, name):
        async with Docker() as docker:
            container = await docker.containers.get(name)
            await container.delete(force=True)

    @classmethod
    async def stop(cls, name):
        async with Docker() as docker:
            container = await docker.containers.get(name)
            await container.stop()

    @classmethod
    async def start(cls, name):
        async with Docker() as docker:
            container = await docker.containers.get(name)
            await container.start()

    @classmethod
    async def logs(cls, name):
        async with Docker() as docker:
            container = await docker.containers.get(name)
            response = ""
            log_response = await container.log(stdout=True, stderr=True)
            return response.join([l for l in log_response])
