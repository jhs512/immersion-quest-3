# Prepared server image for the preflight. Only adds the two Java source files to the
# pinned Temurin 25 JDK (Alpine) base. No CMD: Floci runs `tail -f /dev/null`, and the
# server starts only from user-data.
FROM public.ecr.aws/docker/library/eclipse-temurin@sha256:c7c3d0bdf7f2bbc5a05a6712ed334d198360105634ea9adf76fca94f381b1e3f
LABEL org.opencontainers.image.title="mq-java25-http-guest-preflight"
COPY HelloServer.java HttpCheck.java /opt/mq/
