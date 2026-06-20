FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DATA_DIR=/data
ENV FLAMEGRAPH_DIR=/opt/FlameGraph
ENV WINDOW_SECONDS=60
ENV RETENTION_HOURS=24
ENV SAMPLE_FREQ=99
ENV PERF_EVENT=cpu-clock
ENV PERF_SCOPE=system
ENV START_COLLECTOR=1

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      git \
      perl \
      procps \
      python3 \
      python3-flask \
      stress-ng; \
    (apt-get install -y --no-install-recommends linux-tools-common linux-tools-generic || \
     apt-get install -y --no-install-recommends linux-perf || true); \
    git clone --depth 1 https://github.com/brendangregg/FlameGraph.git /opt/FlameGraph || true; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY profiler /app/profiler
COPY static /app/static
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080
VOLUME ["/data"]

ENTRYPOINT ["/entrypoint.sh"]

