FROM quay.io/bluecat/gateway:22.4.1
USER root

ENV PERMISSION_PATH         "./workflows/device_registration/deployment/permissions.json"

# Copy workflows to gateway
COPY  --chown=flask:root     ./workflows                 /builtin/workflows
COPY  --chown=flask:root     ${PERMISSION_PATH}          /builtin

RUN if [ -s "/builtin/workflows/device_registration/requirements.txt"  ]; then \
       pip3 install -r "/builtin/workflows/device_registration/requirements.txt" ; \
    fi && \
    echo DONE

USER flask
