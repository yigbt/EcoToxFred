# SPDX-FileCopyrightText: 2024 Helmholtz Centre for Environmental Research (UFZ)
#
# SPDX-License-Identifier: AGPL-3.0-only

FROM python:3.13-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.13-slim

LABEL description="EcotoxFred Application"

# Combine user creation, system updates and pip installation into one layer
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r ecotoxfred && \
    useradd -r -g ecotoxfred -m -d /home/ecotoxfred -s /bin/sh -c "ecotoxfred User" ecotoxfred

WORKDIR /app

# Combine COPY and pip operations
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    mkdir -p /app/.config/matplotlib && \
    chown -R ecotoxfred:ecotoxfred /app

ENV MPLCONFIGDIR /app/.config/matplotlib

USER ecotoxfred

# Copy your source code to image workdir and set ownership  
COPY --chown=ecotoxfred:ecotoxfred *.py .
COPY --chown=ecotoxfred:ecotoxfred figures/ figures/
COPY --chown=ecotoxfred:ecotoxfred tools/ tools/
COPY --chown=ecotoxfred:ecotoxfred prompts/ prompts/
COPY --chown=ecotoxfred:ecotoxfred values.yaml .


# indicates the container port, which is exposed to the host
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "bot.py", "--server.port=8501", "--server.address=0.0.0.0"]
