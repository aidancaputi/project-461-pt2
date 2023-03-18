//use git2::Repository;
//use std::fs;
use octocrab::Octocrab;
use std::sync::Arc;
//use std::path::Path;
//use std::io;
//use std::io::BufRead;


pub fn calculate_correctness(url: &str) -> f32 {
    simple_log::info!("Calculating Correctness Score.");
    let starrating = calc_stars(url);
   // let assertrating = calc_asserts(url);
    let result = starrating; 
    result
}

#[tokio::main]
async fn calc_stars(url: &str) -> f32 {
    
    let stars: f32 = make_star_request(url).await;
    simple_log::info!("Calculating Final Correctness value.");
    let fitted = 1_f32 - (1.1_f32).powf(-0.0012 * stars);
    fitted
}

async fn make_star_request(url: &str) -> f32 {
    simple_log::info!("Finding Number of Stars from GitHub API.");
    let v: Vec<&str> = url[19..].split('/').collect();
    let owner: &str = v.get(0).unwrap();
    let repo: &str = v.get(1).unwrap();
    let query = format!("query{{repository(owner:\"{owner}\", name:\"{repo}\"){{stargazerCount}}}}");
    let token = std::env::var("GITHUB_TOKEN");
    let octocrab = match token {
        Ok(t) => Arc::new(Octocrab::builder().personal_token(t).build().unwrap()),
        Err(_e) => panic!("Unable to authenticate with github token (check env variables)"),
    };
    let response: serde_json::Value = octocrab
    .graphql(&query)
    .await
    .expect("Error at call");
    let number = response["data"]["repository"]["stargazerCount"].as_u64().unwrap();
    number as f32
}

/* 
fn calc_asserts(url: &str) -> f32 {
    println!("started cloning...");
    clone_repo(url);
    println!("finished cloning...");
   // traverse_for_sloc();
    let path = Path::new("/repos");
    visit_dirs(&path);
    delete_repo();
    1.0
}
*/

/* 
fn traverse_for_sloc() {
    let current_dir = Path::new(".\\repos");
    for entry in fs::read_dir(current_dir) {
        let entry = (*entry).unwrap();
        let path = entry.path();

        let metadata = fs::metadata(&path).unwrap();
        println!("{:#?}", metadata.file_type());
    }
}
*/

/* 
fn visit_dirs(dir: &Path) -> io::Result<i32> {
    let mut cnt = 0;
  //  let jsstr: str = ".js";
    if dir.is_dir() {
        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.is_dir() {
                visit_dirs(&path)?;
            } else {
                let name: &str = path.file_name().unwrap().to_str().unwrap();
                let v: Vec<&str> = (name).split('.').collect();
                if v.last().unwrap() == (&".js") {
                    println!("called");
                    cnt = cnt + count_lines(name);
                }
            }
            
        }
    }
    Ok(cnt)
}
*/


/* 
fn count_lines(filename: &str) -> i32 {
    println!("{}", filename);
    let file = io::BufReader::new(fs::File::open(filename).expect("Unable to open file"));
    let mut cnt  = 0;
    
    for _ in file.lines() {
        cnt = cnt + 1;
    }
    
    println!("Total lines are: {}",cnt);
    cnt
}
*/

/* 
fn clone_repo(url: &str) {
     let _file = match fs::create_dir_all("./src/rate_repos/metrics/repos") {
        Ok(_file) => _file,
        Err(e) => panic!("failed to create temporary directory: {}", e),
    };
    let _repo = match Repository::clone(url, "./src/rate_repos/metrics/repos") {
        Ok(_repo) => _repo,
        Err(e) => panic!("failed to clone: {}", e),
    };
}

fn delete_repo() {
    let _file = match fs::remove_dir_all("./src/rate_repos/metrics/repos") {
        Ok(_file) => _file,
        Err(e) => panic!("failed to remove temporary directory: {}", e),
    };
}

*/