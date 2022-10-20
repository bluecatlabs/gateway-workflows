FROM quay.io/bluecat/gateway:22.4.1
USER root

ENV PERMISSION_PATH         "./workflows/Network Address Manager/deployment/permissions.json"
ENV CONFIG_PATH             "./workflows/Network Address Manager/deployment/config.py"

# Copy workflows to gateway
COPY  --chown=flask:root     ./workflows                 /builtin/workflows
COPY  --chown=flask:root     ${PERMISSION_PATH}          /builtin
COPY  --chown=flask:root     ${CONFIG_PATH}              /builtin

RUN if [ -s "/builtin/workflows/Network Address Manager/requirements.txt"  ]; then \
       pip3 install -r "/builtin/workflows/Network Address Manager/requirements.txt" ; \
    fi && \
    echo DONE

USER flask

