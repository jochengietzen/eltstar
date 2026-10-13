ARG UV_VERSION=0.8.12


FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv


FROM mcr.microsoft.com/vscode/devcontainers/python:3.13-bullseye

ARG venv_path=/python_venv



COPY ./.zshrc /tmp/.zshrc
COPY --from=uv --chown=root: /uv /uvx /bin/

# Remove broken Yarn repo
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && rm -f /usr/share/keyrings/yarnkey.gpg

RUN apt-get update && apt-get install --no-upgrade  -y sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN pip install pipx
RUN pipx install --global rust-just pre-commit

