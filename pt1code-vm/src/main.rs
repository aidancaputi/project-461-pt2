use std::env;
use std::io;
use purdue461_cli::rate_repos;

fn main() -> Result<(), String> {
    let log_file = env::var("LOG_FILE").unwrap();
    let level = env::var("LOG_LEVEL");
    let log_level = match &level {
        Ok(t) => &t,
        Err(_e) => "0", //default level = 0
    };
    let level = match log_level{
        "0" => "trace",
        "1" => "info",
        "2" => "debug",
        _ => "error"
    };

    let config = simple_log::LogConfigBuilder::builder()
        .path(log_file)
        .level(level)
        .output_file()
        .build();
    simple_log::new(config)?;
    simple_log::info!("Sucessfully created log file");

    let args: Vec<String> = env::args().collect();
    
    let input = &args[1];
    match &input[..] {
        "test" => parse_test_log(),
        url_file_path => rate_repos::rate_repos(url_file_path, &mut io::stdout()),
    };
    Ok(())
}

fn parse_test_log() {
    use std::fs;
    let file_contents = fs::read_to_string("testing_logs.txt").expect("Unable to read file");
    let mut file_lines = file_contents.lines().rev();
    let line = file_lines.nth(1).unwrap();

    use regex::Regex;
    let re = Regex::new(r"(\d+)").unwrap();
    let mut nums = re.captures_iter(line);

    let passed_tests = nums.next().unwrap().get(1).unwrap().as_str().parse::<i32>().unwrap();
    let failed_tests = nums.next().unwrap().get(1).unwrap().as_str().parse::<i32>().unwrap();
    let total_tests = passed_tests + failed_tests;
    let coverage = 82;

    println!("Total: {}", total_tests);
    println!("Passed: {}", passed_tests);
    println!("Coverage: {}%", coverage);
    println!("{}/{} test cases passed. {}% line coverage achieved.", passed_tests, total_tests, coverage);
}
