# Flink runtime with the transform job baked in at /opt/flink/usrlib.
# The same image runs the JobManager, the TaskManager and the one-shot submitter.
FROM eclipse-temurin:21-jdk AS build
WORKDIR /w
COPY gradlew settings.gradle.kts build.gradle.kts ./
COPY gradle ./gradle
# Dependencies first, in their own layer: a code change does not re-download them.
RUN sh ./gradlew --no-daemon -q dependencies > /dev/null
COPY src ./src
RUN sh ./gradlew --no-daemon -q shadowJar -x test

FROM flink:2.3-java21
# Checkpoints/savepoints live here. Created owned by `flink` so a fresh named
# volume inherits that owner — otherwise the JobMaster cannot write checkpoints.
USER root
RUN mkdir -p /flink-data && chown flink:flink /flink-data
USER flink
COPY --from=build /w/build/libs/vnmd-transform.jar /opt/flink/usrlib/vnmd-transform.jar
