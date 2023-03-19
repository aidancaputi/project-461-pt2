# Use the official Rust image.
# https://hub.docker.com/_/rust
FROM rust:1.68.0

# Copy local code to the container image.
WORKDIR /usr/src/app
COPY . .

ENV GITHUB_TOKEN=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
ENV LOG_FILE=log.txt
ENV LOG_LEVEL=0

# Install production dependencies and build a release artifact.
RUN cargo install --path .

# Run the web service on container startup.
CMD ["pt1-code"]