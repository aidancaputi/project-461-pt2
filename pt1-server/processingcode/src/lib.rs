pub mod rate_repos {

    use serde::{Serialize, Deserialize};
    //use std::io;

    pub mod metrics {
        use super::*;

        pub mod bus_factor;
        pub mod correctness;
        //pub mod license;
        pub mod ramp_up;
        pub mod responsive_maintainer;
        use bus_factor::bus_factor_score;
        use responsive_maintainer::responsive_maintainer_score;
        use correctness::calculate_correctness;

        fn round_to_3(score: f32) -> f32 {
            return (score * 1000.0).floor() / 1000.0
        }

        #[derive(Serialize, Deserialize, Debug)]
        //#[serde(rename_all = "UPPERCASE")]
        pub struct MetricScores {
            pub BusFactor: f32,
            pub Correctness: f32,
            pub RampUp: i32,
            pub ResponsiveMaintainer: f32,
            pub LicenseScore: i32,
            pub GoodPinningPractice: i32,
            pub PullRequest: i32,
            pub NetScore: f32,
        }

        const BUS_FACTOR_WEIGHT: f32 = 0.3;
        const CORRECTNESS_WEIGHT: f32 = 0.3;
        const LICENSE_WEIGHT: i32 = 0;
        const RAMP_UP_WEIGHT: i32 = 0;
        const RESPONSIVE_MAINTAINER_WEIGHT: f32 = 0.4;

        pub async fn get_metrics(_url: &str) -> MetricScores {
            // each of these 0.5's will be a call each metric function in their file
            let mut scores = MetricScores {
                BusFactor: bus_factor_score(_url).await,
                Correctness: calculate_correctness(_url).await as f32,
                RampUp: -1,
                ResponsiveMaintainer: responsive_maintainer_score(_url).await,
                LicenseScore: -1,
                GoodPinningPractice: -1,
                PullRequest: -1,
                NetScore: 0.0,
            };

            scores.NetScore = scores.BusFactor * BUS_FACTOR_WEIGHT
                + scores.Correctness * CORRECTNESS_WEIGHT
                + (scores.LicenseScore * LICENSE_WEIGHT) as f32
                + scores.ResponsiveMaintainer * RESPONSIVE_MAINTAINER_WEIGHT
                + (scores.RampUp * RAMP_UP_WEIGHT) as f32;

            // round each score
            scores.NetScore = round_to_3(scores.NetScore);
            scores.Correctness = round_to_3(scores.Correctness);
            scores.BusFactor = round_to_3(scores.BusFactor);
            scores.ResponsiveMaintainer = round_to_3(scores.ResponsiveMaintainer);

            return scores;
        }
    }

    #[derive(Serialize, Deserialize, Debug)]
    //#[serde(rename_all = "UPPERCASE")]
    pub struct UrlSpecs {
        //pub url: String,
        #[serde(flatten)]
        pub metric_scores: metrics::MetricScores,
    }

    fn get_github_url_for_npm(npm_url: &str) -> Result<String, ureq::Error> {
        let url = format!("https://registry.npmjs.org/{}", &npm_url[30..]);
        let json: serde_json::Value = ureq::get(&url).call()?.into_json()?;
        let repo_info = &json["repository"];

        if repo_info["type"] == "git" {
            let mut github_url = repo_info["url"].as_str().unwrap()[4..].to_string();
            if &github_url[..10] == "ssh://git@" {
                github_url = github_url[10..].to_string();
                github_url = format!("https://{github_url}");
            }
            else if &github_url[..2] == "//" {
                github_url = format!("https:{github_url}");
            }
            for _i in 1..5 {
                github_url.pop();
            }
            return Ok(github_url);
        } else {
            return Ok("".to_string());
        }
    }

    pub async fn rate_repos(url: &str) -> String{
        //use std::fs;
        simple_log::info!("Parsing url file.");
        
        //open file and get urls from it
        //let file_contents = fs::read_to_string(url_file_path).expect("Unable to read file");
        //let urls = file_contents.lines();

        let mut url_specs: Vec<UrlSpecs> = Vec::new();

        simple_log::info!("Obtaining github urls.");
        simple_log::info!("Calling metric score calculation functions.");
        //for url in urls {
            if &url[0..22] == "https://www.npmjs.com/" {
                let github_url = get_github_url_for_npm(&url).unwrap();
                if &github_url[0..19] == "https://github.com/" {
                    // if validate_github_url(&github_url).unwrap() {
                        let url_spec = UrlSpecs {
                            //url: url.to_string(),
                            metric_scores: metrics::get_metrics(&github_url).await,
                        };
                        url_specs.push(url_spec);
                }
            }
            else if &url[0..19] == "https://github.com/" {
                // /if validate_github_url(&url).unwrap() {
                    let url_spec = UrlSpecs {
                        //url: url.to_string(),
                        metric_scores: metrics::get_metrics(&url).await,
                    };
                    url_specs.push(url_spec);
            }
            else {
                let url_spec = UrlSpecs {
                    //url: url.to_string(),
                    metric_scores: metrics::MetricScores {
                        BusFactor: 0.0,
                        Correctness: 0.0,
                        RampUp: -1,
                        ResponsiveMaintainer: 0.0,
                        LicenseScore: -1,
                        GoodPinningPractice: -1,
                        PullRequest: -1,
                        NetScore: 0.0,
                    },
                };
                url_specs.push(url_spec);
            }
        //}

        // sort the repos in decreasing order
        simple_log::info!("Sorting repos in decreasing order.");
        url_specs.sort_by(|a, b| {
            b.metric_scores
                .NetScore
                .partial_cmp(&a.metric_scores.NetScore)
                .unwrap()
        });


        simple_log::info!("Printing final score calculations.");
        //print_url_specs(&url_specs, stdout);
        
        return serde_json::to_string(&url_specs).unwrap();
    }

    /*  pub fn print_url_specs(url_specs: &Vec<UrlSpecs>, stdout: &mut dyn io::Write) {
        for repo_info in url_specs {
            writeln!(stdout, "{}", serde_json::to_string(&repo_info).unwrap()).unwrap();
        }
    }  */
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_urls_1() {
        let json_output = br#"{"URL":"https://www.npmjs.com/package/axios","NET_SCORE":0.782,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.999,"BUS_FACTOR_SCORE":0.392,"RESPONSIVE_MAINTAINER_SCORE":0.669,"LICENSE_SCORE":-1}
{"URL":"https://www.npmjs.com/package/karma","NET_SCORE":0.66,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.741,"BUS_FACTOR_SCORE":0.392,"RESPONSIVE_MAINTAINER_SCORE":0.583,"LICENSE_SCORE":-1}
{"URL":"https://www.npmjs.com/package/lodash","NET_SCORE":0.624,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.998,"BUS_FACTOR_SCORE":0.5,"RESPONSIVE_MAINTAINER_SCORE":0.141,"LICENSE_SCORE":-1}
{"URL":"https://www.npmjs.com/package/cloudinary","NET_SCORE":0.54,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.063,"BUS_FACTOR_SCORE":0.244,"RESPONSIVE_MAINTAINER_SCORE":0.419,"LICENSE_SCORE":-1}
"#;
        let mut stdout = Vec::new();
        rate_repos::rate_repos("test_urls_1.txt", &mut stdout);
        assert_eq!(stdout, json_output);
    }

    #[test]
    fn test_urls_2() {
        let json_output = br#"{"URL":"https://www.npmjs.com/package/express","NET_SCORE":0.732,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.998,"BUS_FACTOR_SCORE":0.5,"RESPONSIVE_MAINTAINER_SCORE":0.831,"LICENSE_SCORE":-1}
{"URL":"https://www.npmjs.com/package/mocha","NET_SCORE":0.613,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.918,"BUS_FACTOR_SCORE":0.5,"RESPONSIVE_MAINTAINER_SCORE":0.575,"LICENSE_SCORE":-1}
{"URL":"https://www.npmjs.com/package/pm2","NET_SCORE":0.611,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.987,"BUS_FACTOR_SCORE":0.392,"RESPONSIVE_MAINTAINER_SCORE":0.534,"LICENSE_SCORE":-1}
{"URL":"https://www.npmjs.com/package/async","NET_SCORE":0.568,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.958,"BUS_FACTOR_SCORE":0.392,"RESPONSIVE_MAINTAINER_SCORE":0.441,"LICENSE_SCORE":-1}
{"URL":"https://www.npmjs.com/package/grunt","NET_SCORE":0.514,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.751,"BUS_FACTOR_SCORE":0.5,"RESPONSIVE_MAINTAINER_SCORE":0.411,"LICENSE_SCORE":-1}
"#;
        let mut stdout = Vec::new();
        rate_repos::rate_repos("test_urls_2.txt", &mut stdout);
        assert_eq!(stdout, json_output);
    }

    #[test]
    fn test_print_url_specs() {
        let mut mock_url_specs: Vec<rate_repos::UrlSpecs> = Vec::new();
        mock_url_specs.push(
            rate_repos::UrlSpecs {
                url: "fake_url_1".to_string(),
                metric_scores: rate_repos::metrics::MetricScores {
                    BusFactor: 0.5,
                    Correctness: 0.5,
                    RampUp: -1,
                    ResponsiveMaintainer: 0.5,
                    LicenseScore: -1,
                    GoodPinningPractice: -1,
                    PullRequest: -1,
                    NetScore: 0.5,
                },
            }
        );

        mock_url_specs.push(
            rate_repos::UrlSpecs {
                url: "fake_url_2".to_string(),
                metric_scores: rate_repos::metrics::MetricScores {
                    BusFactor: 0.5,
                    Correctness: 0.5,
                    RampUp: -1,                    
                    ResponsiveMaintainer: 0.5,
                    LicenseScore: -1,
                    GoodPinningPractice: -1,
                    PullRequest: -1,
                    NetScore: 0.7,
                },
            }
        );

        // json_output must look like this with the bad indenting for assert to work correctly
        let json_output = br#"{"URL":"fake_url_1","NET_SCORE":0.5,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.5,"BUS_FACTOR_SCORE":0.5,"RESPONSIVE_MAINTAINER_SCORE":0.5,"LICENSE_SCORE":0.5}
{"URL":"fake_url_2","NET_SCORE":0.7,"RAMP_UP_SCORE":-1,"CORRECTNESS_SCORE":0.5,"BUS_FACTOR_SCORE":0.5,"RESPONSIVE_MAINTAINER_SCORE":0.5,"LICENSE_SCORE":0.5}
"#;

        let mut stdout = Vec::new();
        rate_repos::print_url_specs(&mock_url_specs, &mut stdout);
        assert_eq!(stdout, json_output);
    }
}
