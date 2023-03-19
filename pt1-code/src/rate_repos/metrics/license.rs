use inline_python::python;

pub fn get_license(_url: &str) -> f32{
    
    let repo = get_keywords(_url);
    let res = 0;
    
    let token = std::env::var("GITHUB_TOKEN");
    
    python! {
    from github import Github
    import re
    
    g = Github('token) 
    repo = g.get_repo('repo)
    contents = repo.get_contents("README.md") 
    decoded = contents.decoded_content.decode()
    pattern = "(?:^)LGPLv2.1|GNU(?: )?(?:Lesser)? General Public License v2.1(?:$)"
    if(re.search(pattern, decoded)):
        'res = 1
    else:
        'res = 0  
    }

    return res as f32;
}

fn get_keywords(_url: &str) -> &str {
    let repo = &_url[19..];
    repo
}