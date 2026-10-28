plugins {
    java
    id("com.gradleup.shadow") version "8.3.5"
}

group = "vnmd"
version = "1.0.0"

repositories {
    mavenCentral()
}

val flinkVersion = "2.3.0"

dependencies {
    // Provided by the Flink runtime image (flink:2.3-java21).
    compileOnly("org.apache.flink:flink-streaming-java:$flinkVersion")
    compileOnly("org.apache.flink:flink-connector-base:$flinkVersion")

    // The stock flink image ships NO Kafka connector in /opt/flink/lib, so it is
    // bundled here (unshaded kafka-clients). Do not ALSO drop the SQL uber jar into
    // /opt/flink/lib: org.apache.flink.* is parent-first, the two would collide.
    implementation("org.apache.flink:flink-connector-kafka:5.0.0-2.2")
    implementation("com.fasterxml.jackson.core:jackson-databind:2.18.2")

    testImplementation("org.apache.flink:flink-streaming-java:$flinkVersion")
    testImplementation(platform("org.junit:junit-bom:5.11.4"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

tasks.jar {
    manifest {
        attributes["Main-Class"] = "vnmd.transform.Main"
    }
}

tasks.shadowJar {
    archiveBaseName.set("vnmd-transform")
    archiveClassifier.set("")
    archiveVersion.set("")
    mergeServiceFiles()
    // Logging comes from the Flink runtime.
    dependencies {
        exclude(dependency("org.slf4j:.*"))
    }
}

tasks.test {
    useJUnitPlatform()
}
