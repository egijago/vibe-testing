import json
import shutil
import subprocess
import uuid
from typing import List

from sandbox import runtime


class SandboxError(RuntimeError):
    pass


class LocalExecutor:
    def statement_lines(self, source_code: str) -> List[int]:
        return runtime.statement_lines(source_code)

    def covered_lines(self, source_code: str, calls: List[str]) -> List[int]:
        return runtime.covered_lines(source_code, calls)

    def evaluate_calls(self, source_code: str, calls: List[str]) -> List[dict]:
        return runtime.evaluate_calls(source_code, calls)


class DockerExecutor:
    def __init__(self, image: str = "vibe-testing-sandbox:latest", timeout: float = 30,
                 memory: str = "512m", cpus: str = "1", runtime_name: str = None, docker_bin: str = "docker"):
        self.image = image
        self.timeout = timeout
        self.memory = memory
        self.cpus = cpus
        self.runtime_name = runtime_name  # e.g. "runsc" for gVisor
        self.docker_bin = docker_bin
        self._check_ready()

    def statement_lines(self, source_code: str) -> List[int]:
        return self._run({"op": "statement_lines", "source_code": source_code})

    def covered_lines(self, source_code: str, calls: List[str]) -> List[int]:
        try:
            return self._run({"op": "covered_lines", "source_code": source_code, "calls": calls})
        except subprocess.TimeoutExpired:
            # A call that never returns yields no trustworthy coverage; drop it rather than abort the run.
            return []

    def evaluate_calls(self, source_code: str, calls: List[str]) -> List[dict]:
        try:
            return self._run({"op": "evaluate_calls", "source_code": source_code, "calls": calls})
        except subprocess.TimeoutExpired as e:
            raise SandboxError(f"evaluate_calls timed out after {self.timeout}s") from e

    def _check_ready(self):
        if shutil.which(self.docker_bin) is None:
            raise SandboxError(f"'{self.docker_bin}' not found on PATH; install Docker or use --executor exec")
        probe = subprocess.run([self.docker_bin, "image", "inspect", self.image],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if probe.returncode != 0:
            raise SandboxError(f"Sandbox image '{self.image}' not found. "
                               f"Build it with: docker build -t {self.image} sandbox/")

    def _docker_cmd(self, name: str) -> List[str]:
        cmd = [
            self.docker_bin, "run", "--rm", "-i", "--name", name,
            "--network", "none",
            "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,size=64m",
            "--user", "65534:65534",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--memory", self.memory, "--memory-swap", self.memory,
            "--cpus", self.cpus,
            "--pids-limit", "64",
            "--ulimit", "nofile=256:256",
        ]
        if self.runtime_name:
            cmd += ["--runtime", self.runtime_name]
        return cmd + [self.image]

    def _run(self, job: dict):
        name = f"vibe-sandbox-{uuid.uuid4().hex[:12]}"
        try:
            proc = subprocess.run(self._docker_cmd(name), input=json.dumps(job), capture_output=True,
                                  text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            # Killing the docker CLI does not stop the container; remove it explicitly.
            subprocess.run([self.docker_bin, "rm", "-f", name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            raise

        try:
            response = json.loads(proc.stdout)
        except json.JSONDecodeError:
            raise SandboxError(f"Sandbox exited with code {proc.returncode} without a result "
                               f"(OOM-killed or crashed?). stderr: {proc.stderr[-2000:]}")
        if not response.get("ok"):
            raise SandboxError(response.get("error", "unknown sandbox error"))
        return response["result"]


def make_executor(kind: str = "exec", **docker_kwargs):
    """Builds an executor by name; `docker_kwargs` are only used by the docker executor."""
    if kind == "exec":
        return LocalExecutor()
    if kind == "docker":
        return DockerExecutor(**docker_kwargs)
    raise ValueError(f"Unknown executor '{kind}' (expected 'exec' or 'docker')")
