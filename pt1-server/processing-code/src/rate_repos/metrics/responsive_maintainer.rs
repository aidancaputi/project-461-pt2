// Calculate responsive maintainer score based on the average time repository issues are open for
// and the last time the repository was updated
use octocrab::Octocrab;
use std::sync::Arc;
pub fn responsive_maintainer_score(url: &str) -> f32 {
    simple_log::info!("Calculating Responsive Maintainer Score.)");

    let token = std::env::var("GITHUB_TOKEN");
    let octocrab = match token {
        Ok(t) => {
            simple_log::debug!("RM Score: Used Github token.)");
            Arc::new(Octocrab::builder().personal_token(t).build().unwrap())
        }
        Err(_e) => {
            simple_log::debug!("RM Score: Did not use Github token.");
            octocrab::instance()
        }
    };
    simple_log::trace!("Parcing keywords from url.");
    let keywords = get_keywords(url);
    simple_log::trace!("Calculating average time issues remain open for.");
    let avg_time_opened = calc_time_opened(&octocrab, keywords);
    simple_log::trace!("Calculating time since last repository update.");
    let time_since_update = calc_update_time(&octocrab, keywords);
    simple_log::trace!("Calculating final RM Score.");
    let score = calc_rm_score(avg_time_opened, time_since_update);
    score
}

// Calculate the amount of time since the repsository was updated
use ::std::time::SystemTime;
#[tokio::main]
async fn calc_update_time(octocrab: &Octocrab, (owner, repo): (&str, &str)) -> f32 {
    let value = octocrab
        .repos(owner, repo)
        .get_community_profile_metrics()
        .await
        .unwrap();

    let mut time_since_update = 0.0;
    if let Some(updated_at) = value.updated_at {
        let updated_at = updated_at.timestamp() as f32;
        let curr_time = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs_f32();
        time_since_update = (curr_time - updated_at) / (86400.0);

        //normalize time_since_update    1/500 puts 0.5 around 1 year
        time_since_update = f32::exp(-0.002 * time_since_update);
    }
    time_since_update
}

// Calcuate the final responsive maintainer score, weighting average time each issue was open for
// more heavily because this metric more strongly reflects how responsive the repository is to problems
fn calc_rm_score(avg_time_opened: f32, time_since_update: f32) -> f32 {
    0.7 * avg_time_opened + 0.3 * time_since_update
}

// Get the owner name and repository title from the given github url
fn get_keywords(_url: &str) -> (&str, &str) {
    let part_str = &_url[19..];
    let divisionidx = part_str.find("/").expect("Error getting keywords");
    let owner = &part_str[..divisionidx];
    let repo = &part_str[divisionidx + 1..];

    (owner, repo)
}

// Calculate the average time that all closed issues were open for
#[tokio::main]
async fn calc_time_opened(octocrab: &Octocrab, (owner, repo): (&str, &str)) -> f32 {
    // Sample- use one repository and calculate mean issue open time
    let mut count = 0.0;
    let mut total_time_opened = 0.0;
    let mut pgnum = 0 as u32;
    'outer: loop {
        use octocrab::params;
        pgnum += pgnum;
        let value = octocrab
            .issues(owner, repo)
            .list()
            .state(params::State::Closed)
            .per_page(25)
            .page(pgnum)
            .send()
            .await
            .unwrap();

        for issue in value {
            if let Some(closed_at) = issue.closed_at {
                if issue.pull_request == None {
                    // The issue is closed and not a pull request, so calculate time opened and add to total open time (total)
                    let closed_date = closed_at.timestamp();

                    let opened_date = issue.created_at.timestamp();

                    let time_opened = closed_date - opened_date;
                    let sec_to_days = 86400.0;
                    let time_opened = time_opened as f32 / sec_to_days;
                    total_time_opened += time_opened;
                    count += 1.0;
                    if count >= 50.0 {
                        break 'outer;
                    }
                }
            }
        }
    }
    let average_time_opened = total_time_opened / count;

    //normalize average_time_opened to return score between 0 and 1
    //Using the function y = e^(-x/20)- chosen b/c 0.5 is at 2 weeks, 0.25 at 4 weeks
    f32::exp(-0.05 * average_time_opened)

}
