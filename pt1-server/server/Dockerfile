# Use the official Rust image.
# https://hub.docker.com/_/rust
FROM rust:1.63.0

# Copy local code to the container image. for push
WORKDIR /usr/src/app
COPY . .

#ENV GITHUB_TOKEN=''
#ENV LOG_LEVEL='2'
#ENV LOG_FILE="log.txt"

# Install production dependencies and build a release artifact.
#RUN cargo install --path pt1-server/server
RUN cargo build --manifest-path pt1-server/server/Cargo.toml

# Run the web service on container startup.
CMD ["./pt1-server/target/debug/hellorust"]