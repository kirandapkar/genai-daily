# GenAI Daily

One production-quality GenAI project per day. Single repo, one subdirectory per project.

**First-time push:** Create an empty repo `genai-daily` on GitHub, then from this directory:  
`git remote add origin https://github.com/kirandapkar/genai-daily.git && git push -u origin main`

| # | Project | Status |
|---|---------|--------|
| 01 | [production_llm_api_foundation](01-production_llm_api_foundation/) | Done |
| 02 | [llm_api_with_rate_limit_and_cost_tracking](02-llm_api_with_rate_limit_and_cost_tracking/) | Done |
| 03 | [llm_api_multi_model_router](03-llm_api_multi_model_router/) | Done |

## Setup

Each project has its own `requirements.txt` and `.env.example`. Copy `.env.example` to `.env` and add your keys.

## Keys (per project)

- `OPENROUTER_API_KEY` – [OpenRouter](https://openrouter.ai) (free models available)
- `GEMINI_API_KEY` – [Google AI](https://ai.google.dev) (optional, for Gemini models)
