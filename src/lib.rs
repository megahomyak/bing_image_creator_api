pub struct Generator {
    http_client: reqwest::Client,
    pub max_retries: Option<usize>,
}

pub enum CreationError {
    InvalidToken,
    HttpClientCannotBeInitialized(reqwest::Error),
}

pub enum GenerationError {
    GeolocationBlock,
    PromptBlock,
    TooManyRetries,
    GenerationBlock,
    ServerOverload,
    RequestError(reqwest::Error),
}

pub struct GenerationLinks(pub Vec<String>);

impl Generator {
    pub fn new(user_token: &str) -> Result<Self, CreationError> {
        let mut default_headers = reqwest::header::HeaderMap::new();
        default_headers.insert(
            "cookie",
            format!("_U={}", user_token)
                .parse()
                .map_err(|_err| CreationError::InvalidToken)?,
        );
        let http_client = reqwest::Client::builder()
            .default_headers(default_headers)
            .redirect(reqwest::redirect::Policy::none())
            .build()
            .map_err(|err| CreationError::HttpClientCannotBeInitialized(err))?;
        Ok(Self {
            http_client,
            max_retries: None,
        })
    }

    pub async fn generate(&self, prompt: &str) -> Result<GenerationLinks, GenerationError> {
        let response = self
            .http_client
            .post("https://www.bing.com/images/create")
            .query(&[("q", prompt), ("rt", "3")])
            .send()
            .await
            .map_err(|err| GenerationError::RequestError(err))?;
        let Some(response) = response.headers().get("location") else {
            if response.bytes().await.map_err()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
