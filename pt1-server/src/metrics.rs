use serde::{Serialize, Deserialize};
use std::io;

use super::*;

mod bus_factor;
mod correctness;
//pub mod license;
mod ramp_up;
mod responsive_maintainer;
use bus_factor::bus_factor_score;
use responsive_maintainer::responsive_maintainer_score;
use correctness::calculate_correctness;

fn round_to_3(score: f32) -> f32 {
    return (score * 1000.0).floor() / 1000.0
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "UPPERCASE")]
pub struct MetricScores {
    pub net_score: f32,
    pub ramp_up_score: i32,
    pub correctness_score: f32,
    pub bus_factor_score: f32,
    pub responsive_maintainer_score: f32,
    pub license_score: i32,
}

const BUS_FACTOR_WEIGHT: f32 = 0.3;
const CORRECTNESS_WEIGHT: f32 = 0.3;
const LICENSE_WEIGHT: i32 = 0;
const RAMP_UP_WEIGHT: i32 = 0;
const RESPONSIVE_MAINTAINER_WEIGHT: f32 = 0.4;

pub fn get_metrics(_url: &str) -> MetricScores {
    // each of these 0.5's will be a call each metric function in their file
    let mut scores = MetricScores {
        net_score: 0.0,
        ramp_up_score: -1,
        bus_factor_score: bus_factor_score(_url),
        correctness_score: calculate_correctness(_url) as f32,
        responsive_maintainer_score: responsive_maintainer_score(_url),
        license_score: -1,
    };

    scores.net_score = scores.bus_factor_score * BUS_FACTOR_WEIGHT
        + scores.correctness_score * CORRECTNESS_WEIGHT
        + (scores.license_score * LICENSE_WEIGHT) as f32
        + scores.responsive_maintainer_score * RESPONSIVE_MAINTAINER_WEIGHT
        + (scores.ramp_up_score * RAMP_UP_WEIGHT) as f32;

    // round each score
    scores.net_score = round_to_3(scores.net_score);
    scores.correctness_score = round_to_3(scores.correctness_score);
    scores.bus_factor_score = round_to_3(scores.bus_factor_score);
    scores.responsive_maintainer_score = round_to_3(scores.responsive_maintainer_score);

    return scores;
}