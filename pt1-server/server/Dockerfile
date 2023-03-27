# Use the official Rust image.
# https://hub.docker.com/_/rust
FROM rust:1.63.0

ENV APP_HOME /pt1-server/server
WORKDIR $APP_HOME

#copy rest server folder to this image
COPY pt1-server/ ./

# Install production dependencies and build a release artifact.
RUN cargo install --path .

# Run the web service on container startup.
CMD ["hellorust"]