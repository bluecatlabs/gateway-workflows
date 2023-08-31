FROM quay.io/bluecat/gateway_ci:23.2.1
USER root

ENV PERMISSION_PATH         "./workflows/Role Management UI/deployment/permissions.json"
ENV BW_WF                   "bluecat_gateway/workflows/"
ENV BW_RM                   "bluecat_gateway/workflows/Role Management UI"


# Copy workflows to gateway
COPY  --chown=flask:root     ./workflows                    /builtin/workflows
COPY  --chown=flask:root     ${PERMISSION_PATH}             /builtin/permissions.json
COPY  --chown=flask:root     ${BW_WF}                       /bluecat_gateway/workflows
COPY  --chown=flask:root     ${BW_RM}/                     /${BW_RM}/
COPY  --chown=flask:root     ${BW_RM}/config/              /${BW_RM}/config/


RUN if [ -s "/builtin/workflows/Role Management UI/requirements.txt"  ]; then \
    pip3 install -r "/builtin/workflows/Role Management UI/requirements.txt" ; \
    fi && \
    echo DONE
