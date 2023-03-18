use hyper::{
    server::conn::AddrStream,
    service::{make_service_fn, service_fn},
    Body, Request, Response, Server,
};
use std::convert::Infallible;
use std::env;

//trying to import functionality from pt1 code
mod metrics;

#[tokio::main]
async fn main() {
    pretty_env_logger::init();

    let mut port: u16 = 8080;
    match env::var("PORT") {
        Ok(p) => {
            match p.parse::<u16>() {
                Ok(n) => {
                    port = n;
                }
                Err(_e) => {}
            };
        }
        Err(_e) => {}
    };
    let addr = ([0, 0, 0, 0], port).into();

    let make_svc = make_service_fn(|_socket: &AddrStream| async move {
        Ok::<_, Infallible>(service_fn(move |_: Request<Body>| async move {
            let mut hello = "Hey there ".to_string();
            
            //testing a url to see how their pt1 code works
            //let mut test_url = "https://www.npmjs.com/package/express".to_string();
            //let mut test_url_scores = metrics::get_metrics(test_url).to_string();
            
            match env::var("TARGET") {
                Ok(target) => {
                    hello.push_str(&target);
                }
                Err(_e) => hello.push_str("Jerrry"),
            };
            Ok::<_, Infallible>(Response::new(Body::from(hello)))
            //Ok::<_, Infallible>(Response::new(Body::from(test_url_scores)))
        }))
    });

    let server = Server::bind(&addr).serve(make_svc);

    println!("Listening on http://{}", addr);
    if let Err(e) = server.await {
        eprintln!("server error: {}", e);
    }
}