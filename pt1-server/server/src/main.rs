use hyper::{
    server::conn::AddrStream,
    service::{make_service_fn, service_fn},
    Body, Request, Response, Server,
   };
   use std::convert::Infallible;
   use std::env;
   use purdue461_cli;
   //use std::io;
   
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
         Ok::<_, Infallible>(service_fn(move |_req: Request<Body>| async move {
               let mut req_url = &(_req.uri().to_string())[1..];
               println!("{}" , req_url);
               let mut url_metrics = purdue461_cli::rate_repos::rate_repos(req_url).await;
               Ok::<_, Infallible>(Response::new(Body::from(url_metrics)))
         }))
      });
   
      let server = Server::bind(&addr).serve(make_svc); //test
   
      println!("Listening on http://{}", addr);
      if let Err(e) = server.await {
         eprintln!("server error: {}", e);
      }
   }