ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install coverage==7.9.1

COPY runtime.py /opt/sandbox/runtime.py

# Run as unprivileged user
USER 65534:65534
WORKDIR /tmp

# -I: isolated mode
# -B: never write .pyc files (rootfs is read-only)
ENTRYPOINT ["python", "-I", "-B", "/opt/sandbox/runtime.py"]
