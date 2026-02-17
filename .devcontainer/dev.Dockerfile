FROM mcr.microsoft.com/devcontainers/python:3.14-trixie

# Install Node.js, npm, and other dependencies
RUN apt-get update && \
    apt-get install -y \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CDK globally
RUN npm install -g aws-cdk

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip

# Install Pulumi
RUN curl -fsSL https://get.pulumi.com | sh 
# Pulumi gets installed as root, need to move it to a location in the PATH for the vscode user
RUN mkdir /usr/bin/.pulumi && mv /root/.pulumi/* /usr/bin/.pulumi/ 
ENV PATH "$PATH:/usr/bin/.pulumi/bin/"

WORKDIR /tmp
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

ARG USERNAME=vscode
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && mkdir /commandhistory \
    && touch /commandhistory/.bash_history \
    && chown -R $USERNAME /commandhistory \
    && echo "$SNIPPET" >> "/home/$USERNAME/.bashrc"

USER $USERNAME
WORKDIR /workspace